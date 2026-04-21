# Firmware Setup

## Entry project

The primary firmware sketch lives under:

```text
firmware/mpu6050_init/mpu6050_init.ino
```

## Notes

- Keep device network config and upload logic together with the sketch helpers in the same directory.
- Treat firmware secrets and Wi-Fi credentials as local-only values.
