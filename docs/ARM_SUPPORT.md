# Multi-Platform ARM Support

Aphrodite now supports building for both AMD64 and ARM64 architectures.

## Automatic ARM Support (GitHub Actions)

When you create a release, GitHub Actions will automatically build Docker images for both:
- `linux/amd64` (Intel/AMD processors)
- `linux/arm64` (ARM processors including Apple Silicon, Raspberry Pi 4+, AWS Graviton)

The multi-platform images are pushed to the GitHub Container Registry with full manifest support.

## Local Multi-Platform Building

### Prerequisites

1. **Docker Desktop** (recommended) or Docker with buildx plugin
2. **Pre-built frontend** (run `./scripts/build.sh` first)

### Quick Start

```bash
# Linux/macOS
./scripts/build-multiplatform.sh

# Windows PowerShell
.\scripts\build-multiplatform.ps1
```

### Manual Multi-Platform Build

```bash
# Setup multi-platform builder (one-time)
docker buildx create --name aphrodite-builder --driver docker-container --use

# Build for both platforms
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  --tag aphrodite:latest \
  --load \
  .
```

## Platform-Specific Deployment

### ARM64 Devices
- **Apple Silicon Macs**: `docker run -p 8000:8000 ghcr.io/jackkerouac/aphrodite:latest`
- **Raspberry Pi 4+**: Same command (requires 64-bit OS)
- **AWS Graviton**: Deploy normally with docker-compose

### AMD64 Devices
- **Standard x86_64 systems**: Works automatically
- **Existing deployments**: No changes needed

## Registry Push

To push multi-platform images to your own registry:

```bash
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  --push \
  --tag your-registry/aphrodite:latest \
  .
```

## Limitations

- **Local Development**: Docker can only load one platform at a time locally
- **Build Time**: Multi-platform builds take significantly longer
- **Registry Support**: Your registry must support Docker manifest lists

## Troubleshooting

### "no match for platform" Error
Your Docker installation doesn't support the requested platform. Use single-platform build:
```bash
docker build --tag aphrodite:latest .
```

### Buildx Not Available
Install Docker Desktop or enable buildx:
```bash
# Enable buildx (if not available)
docker buildx install
```

### ARM64 Performance
ARM64 builds may be slower on AMD64 hosts due to emulation. For best performance, build on native ARM64 hardware when possible.
