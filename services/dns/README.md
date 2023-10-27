# dns

If you're using systemd-resolve, it may actually be blocking you from using port 53.

If that's the case, need to:

- Disable `DNSStubListener` in `/etc/systemd/resolved.conf`:

  ```sh
  echo "/etc/systemd/resolved.conf" | sudo tee -a /etc/systemd/resolved.conf
  ```

- Use systemd's `resolve.conf`, not it's `stub-resolv.conf`:

  ```sh
  sudo ln -sf /run/systemd/resolve/resolv.conf /etc/resolv.conf
  ```

- Restart `systemd-resolved.service`:

  ```sh
  sudo systemctl restart systemd-resolved.service
  ```

## Combining with Tailscale

You can combine this with Tailscale to access your services from outside of your home. To do this, follow the Tailscale guide, and when you've got that set up, go to the DNS tab.

Add a Custom Name Server, and enter the Tailscale IP for your homelab machine (you can find this IP in the Machines tab of Tailscale). You can restrict it to `{{HOMELAB_BASE_DOMAIN}}` (but you won't get access to your ad-blocking DNS).

Once you've added your DNS server, make sure "Override local DNS" is turned on.

Now, any of your devices with Tailscale can access any of your services via their "External Access" link.
