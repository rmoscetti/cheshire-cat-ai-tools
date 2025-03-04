# builder image
FROM python:3.13-slim AS builder
# Install dependencies and build the project
RUN pip install hatch

WORKDIR /app
COPY . /app
RUN hatch build

# # Final image
FROM python:3.13-slim
WORKDIR /app
# # Copy the built artifacts from the builder container
RUN pip install uvicorn
COPY --from=builder /app/dist/*.whl /app/
RUN pip install /app/*.whl
# COPY . /app
# RUN pip install -e .

EXPOSE 8000


CMD ["uvicorn", "drymulator.server:app", "--host", "0.0.0.0", "--port", "8000"]