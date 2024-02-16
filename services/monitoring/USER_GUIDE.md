### Monitoring

Powered by [Grafana](https://grafana.com/), [Prometheus](https://prometheus.io/), and [cadvisor](https://github.com/google/cadvisor)

- External Access: https://monitoring.{{env.Getenv "HOMELAB_BASE_DOMAIN"}}
- External Access: https://cadvisor.{{env.Getenv "HOMELAB_BASE_DOMAIN"}}

This is mostly nerdy stats, but also comes in handy if you ever want to see how your homelab is performing over time.

#### Recommended Dashboards:

Visit https://grafana.{{env.Getenv "HOMELAB_BASE_DOMAIN"}}/dashboard/import to import dashboards.

- [Node Exporter Full](https://grafana.com/grafana/dashboards/1860-node-exporter-full/)
- [Docker monitoring](https://grafana.com/grafana/dashboards/193-docker-monitoring/)
