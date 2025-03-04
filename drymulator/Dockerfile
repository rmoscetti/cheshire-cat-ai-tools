# builder image
FROM python:3.13-slim AS builder
WORKDIR /app
COPY . /app

# Install dependencies and build the project
RUN pip install hatch
RUN hatch build

# # Final image
FROM python:3.13-slim
WORKDIR /app
# # Copy the built artifacts from the builder container
COPY --from=builder /app/dist/*.whl /app/
RUN pip install /app/*.whl
# COPY . /app
# RUN pip install -e .

RUN pip install uvicorn
EXPOSE 8000


CMD ["uvicorn", "drymulator.server:app", "--host", "0.0.0.0", "--port", "8000"]