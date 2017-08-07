# This file needs to be copied to ansible module_utils
try:
    import imcsdk
    HAS_IMCSDK = True
except:
    HAS_IMCSDK = False


class ImcConnection():

    @staticmethod
    def is_login_param(param):
        return param in [
            "ip",
            "username",
            "password",
            "port",
            "secure",
            "proxy",
            "server",
            "starship_options"]

    def __init__(self, module):
        if HAS_IMCSDK is False:
            results = {}
            results["msg"] = "imcsdk is not installed"
            module.fail_json(**results)
        self.module = module
        self.handle = None

    def login(self):
        from imcsdk.imchandle import ImcHandle
        ansible = self.module.params

        starship_options = ansible.get('starship_options')
        if starship_options:
            server = ImcHandle("192.168.1.1", "admin", "password")
            server.set_starship_proxy(starship_options["url"])
            server.set_starship_headers(starship_options["cookies"])
            return server

        server = ansible.get('server')
        if server:
            return server

        results = {}
        try:
            server = ImcHandle(ip=ansible["ip"],
                               username=ansible["username"],
                               password=ansible["password"],
                               port=ansible["port"],
                               secure=ansible["secure"],
                               proxy=ansible["proxy"])
            server.login()
        except Exception as e:
            results["msg"] = str(e)
            self.module.fail_json(**results)
        self.handle = server
        return server

    def logout(self):
        ansible = self.module.params

        starship_options = ansible.get('starship_options')
        if starship_options:
            return True

        server = ansible.get('server')
        if server:
            # we used a pre-existing handle from a task.
            # do not logout
            return False

        if self.handle:
            self.handle.logout()
            return True
        return False
