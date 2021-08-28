## Запуск

```docker-compose up -d --build```

#### В ряде случаем под виндой может потрубоваться:
```sysctl net.ipv4.conf.all.forwarding=1```

```sudo iptables -P FORWARD ACCEPT```