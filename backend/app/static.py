from fastapi.staticfiles import StaticFiles

# Serve local images folder
app.mount(
    "/local-images",
    StaticFiles(directory="E:/pothole-system/backend/backend_output_images"),
    name="local-images"
)
