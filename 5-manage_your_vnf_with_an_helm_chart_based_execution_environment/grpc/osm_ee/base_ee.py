import asyncio
import logging
import yaml
import os

from osm_ee.vnf_ee import VnfEE
from dotenv import set_key
import osm_ee.utils as utils
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

class BaseEE:

    RETURN_STATUS_LIST = ["OK", "PROCESSING", "ERROR"]
    CONFIG_FILE = "/app/storage/config.yaml"
    ENV_CONFIG_FILE = "/app/storage/config.env"
    SSH_KEY_FILE = "~/.ssh/id_rsa"
    HEALTH_CHECK_ACTION = "health-check"

    def __init__(self):
        self.logger = logging.getLogger('base')
        self.logger_ee = logging.getLogger('osm_ee.vnf')

        # Check if configuration is stored and load it
        if os.path.exists(self.CONFIG_FILE):
            with open(self.CONFIG_FILE, 'r') as file:
                self.config_params = yaml.load(file, Loader=yaml.FullLoader)
                self.logger.debug("Load existing config from file: {}".format(self.config_params))
        else:
            self.config_params = {}

        self.vnf_ee = VnfEE(self.config_params)

    async def get_ssh_key(self):
        """
        Retrieved from https://github.com/ATNoG/osm-ansible-ee
        """
        self.logger.debug("Obtain ssh key")
        self.logger_ee.debug("Obtain ssh key")
        priv_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )

        encrypted_pem_private_key = priv_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )

        pub_key = priv_key.public_key().public_bytes(
            encoding=serialization.Encoding.OpenSSH,
            format=serialization.PublicFormat.OpenSSH
        )

        with open(os.path.expanduser(self.SSH_KEY_FILE), "w") as priv_key_file:
            priv_key_file.write(encrypted_pem_private_key.decode())
            priv_key_file.close()

        with open(os.path.expanduser(self.SSH_KEY_FILE) + ".pub", "w") as pub_key_file:
            pub_key_file.write(pub_key.decode())
            pub_key_file.close()
        
        self.logger.debug("ssh pub-key: {}".format(pub_key.decode()))    
        self.logger_ee.debug("ssh-key: {}".format(pub_key.decode()))
       
        #await change_permissions()
        return pub_key.decode()

    async def run_action(self, id, name, params):
        self.logger.debug("Execute action id: {}, name: {}, params: {}".format(id, name, params))

        try:
            # Health-check
            if name == self.HEALTH_CHECK_ACTION:
                yield "OK", "Health-check ok"
            else:

                # Obtain dynamically code to be executed
                method = getattr(self.vnf_ee, name)

                # Convert params from yaml format
                action_params = yaml.safe_load(params)

                if name == "config":
                    self.logger.debug("Store config info in file: {}".format(self.CONFIG_FILE))
                    self.logger_ee.debug("Store config info in file: {}".format(self.CONFIG_FILE))
                    self.config_params.update(action_params)
                    with open(self.CONFIG_FILE, 'w') as file:
                        config = yaml.dump(self.config_params, file)
                    with open(self.ENV_CONFIG_FILE, "w") as f:
                        for k, v in self.config_params.items():
                            k = k.replace("-","")
                            self.logger.debug(f"Writing")
                            self.logger_ee.debug(f"Writing")
                            f.write(f"{k}={v}\n")
                    os.chmod(os.path.expanduser(self.SSH_KEY_FILE), 0o600)
                    target_ip = self.config_params['ssh-hostname']
                    await utils.add_host(target_ip)
                    
                async for return_status, detailed_message in method(id, action_params):
                    if return_status not in self.RETURN_STATUS_LIST:
                        yield "ERROR", "Invalid return status"
                    else:
                        yield return_status, str(detailed_message)
        except AttributeError as e:
            error_msg = "Action name: {} not implemented".format(name)
            self.logger.error(error_msg)
            yield "ERROR", error_msg
        except Exception as e:
            self.logger.error("Error executing action id, name: {},{}: {}".format(id, name, str(e)), exc_info=True)
            yield "ERROR", str(e)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    loop = asyncio.get_event_loop()
    try:
        ee = BaseEE()
        id = "test1"
        name = "touch2"
        params = {"file_path": "/var/tmp/testfile1.txt"}
        action = asyncio.ensure_future(ee.run_action(id, name, params))
        loop.run_until_complete(action)
    finally:
        loop.close()
