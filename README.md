# SSH jumphost config generator

This tool generates a ~/.ssh/config file based on host definitions in a yaml file in the following format:

```yaml
# ~/.ssh/hostinfo.yml

brixit:
    host: brixit.example.com # Public hostname/ip of the jumphost
    user: jump # Username on the jumphost
    prefix: "192.168.2." # The subnet containing the vm's
    subhosts:
        101: data # This makes a definition for brixit.data on 192.168.2.101
        102: mail
        103: example

otherserver:
    host: other.example.com
    user: example
    prefix: "172.16.42."
    subhosts:
        101: example
        102: example2
        254: router
```

And generates this ssh config:

```
Host otherserver
        User example
        Hostname other.example.com
        IdentityFile ~/.ssh/brixit_rsa

Host otherserver.example2
        User root
        Hostname 172.16.42.102
        ProxyCommand ssh otherserver netcat -w 120 %h %p
        IdentityFile ~/.ssh/brixit_rsa

Host otherserver.example
        User root
        Hostname 172.16.42.101
        ProxyCommand ssh otherserver netcat -w 120 %h %p
        IdentityFile ~/.ssh/brixit_rsa

Host otherserver.router
        User root
        Hostname 172.16.42.254
        ProxyCommand ssh otherserver netcat -w 120 %h %p
        IdentityFile ~/.ssh/brixit_rsa

Host brixit
        User jump
        Hostname brixit.example.com
        IdentityFile ~/.ssh/brixit_rsa

Host brixit.data
        User root
        Hostname 192.168.2.101
        ProxyCommand ssh brixit netcat -w 120 %h %p
        IdentityFile ~/.ssh/brixit_rsa

Host brixit.mail
        User root
        Hostname 192.168.2.102
        ProxyCommand ssh brixit netcat -w 120 %h %p
        IdentityFile ~/.ssh/brixit_rsa

Host brixit.example
        User root
        Hostname 192.168.2.103
        ProxyCommand ssh brixit netcat -w 120 %h %p
        IdentityFile ~/.ssh/brixit_rsa

```

If you move your original ~/.ssh/config to ~/.ssh/config.pre it will be prepended to the generated config file.
