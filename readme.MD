## Запуск

```docker-compose up -d --build```

#### В ряде случаем под виндой может потребоваться:
```sysctl net.ipv4.conf.all.forwarding=1```

```sudo iptables -P FORWARD ACCEPT```