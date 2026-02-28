Given these requirements and schema / api information, can you create a detailed list of user stories and their corresponding tasks that you will need to perform to achieve the requirements. Make the tasks granular, one task is one operation.

Requirements:

Infrastructure as Code & CI/CD

**Goal:** Automate the deployment process to Azure, maintaining strict isolation between the Test and Production environments.

* **Requirements:**
* Write Terraform configuration files utilizing variables to provision distinct Azure Resource Groups, Azure Container Apps, and Azure Database for PostgreSQL servers.
* Create a GitHub Actions workflow that builds the Docker images and pushes them to an Azure Container Registry (ACR).
* Configure the CI/CD pipeline to automatically apply Terraform and deploy to the `Test` environment on merge to `main`, with a manual approval step required to deploy to `Prod`.


* **Deliverables:**
| Component | Deliverable Description |
| :--- | :--- |
| **Terraform** | `main.tf`, `variables.tf`, `test.tfvars`, and `prod.tfvars`. |
| **CI/CD** | `.github/workflows/deploy.yml` defining the build, test-deploy, and prod-deploy jobs. |

---

Here is the granular, operation-by-operation breakdown of user stories and tasks for Feature 7 (Infrastructure as Code & CI/CD).

This final phase brings your application out of the local development environment and securely into the cloud, establishing professional-grade deployment pipelines.

### User Story 1: Production-Ready Dockerization

**"As a DevOps engineer, I need production-optimized Dockerfiles for the frontend and backend so that the deployed containers are secure, lightweight, and performant."**

* **Task 1.1:** Create `Dockerfile.prod` in the `/backend` directory.
* **Task 1.2:** Configure the backend `Dockerfile.prod` to use a multi-stage build, installing dependencies in a builder stage and copying them to a minimal Python runtime image.
* **Task 1.3:** Set the CMD in the backend `Dockerfile.prod` to use Gunicorn with Uvicorn workers (`gunicorn -k uvicorn.workers.UvicornWorker`) instead of the development reloader.
* **Task 1.4:** Create `Dockerfile.prod` in the `/frontend` directory using a multi-stage build.
* **Task 1.5:** Configure the frontend builder stage to run `npm run build` to generate the static assets.
* **Task 1.6:** Configure the frontend final stage to use a lightweight Nginx image (e.g., `nginx:alpine`), copy the static assets from the builder stage into `/usr/share/nginx/html`, and copy a custom `nginx.conf` to handle React Router fallbacks.

### User Story 2: Terraform State & Azure Foundation

**"As an infrastructure administrator, I want to define the base Azure resources and remote state storage so that my infrastructure is tracked and manageable via code."**

* **Task 2.1:** Create an `infrastructure/` directory at the root of the project.
* **Task 2.2:** Manually create an Azure Storage Account and Blob Container via the Azure CLI to act as the remote backend for Terraform state files.
* **Task 2.3:** Create `infrastructure/main.tf` and define the `terraform` block, configuring the `azurerm` provider and the remote `backend "azurerm"`.
* **Task 2.4:** Create `infrastructure/variables.tf` to define all required input variables (e.g., `environment`, `location`, `db_username`, `db_password`, `gemini_api_key`).
* **Task 2.5:** Create `infrastructure/test.tfvars` assigning values for the Test environment (e.g., `environment = "test"`, using cheaper database SKUs).
* **Task 2.6:** Create `infrastructure/prod.tfvars` assigning values for the Prod environment (e.g., `environment = "prod"`, using production-grade SKUs).
* **Task 2.7:** Add a resource block in `main.tf` to provision the Azure Resource Group based on the `environment` variable (e.g., `rg-stockapp-${var.environment}`).

### User Story 3: Azure Database & Container Registry Provisioning

**"As an infrastructure administrator, I need a managed PostgreSQL instance and a private container registry so that the app has persistent storage and a secure place to pull images."**

* **Task 3.1:** Add an `azurerm_container_registry` resource block to `main.tf` to provision an Azure Container Registry (ACR). Enable the admin user for deployment access.
* **Task 3.2:** Add an `azurerm_postgresql_flexible_server` resource block to `main.tf` to provision the managed PostgreSQL database.
* **Task 3.3:** Configure the PostgreSQL server SKU, storage size, and backup retention policies dynamically using the variables defined in `variables.tf`.
* **Task 3.4:** Add an `azurerm_postgresql_flexible_server_firewall_rule` resource block to allow internal Azure services (like Container Apps) to access the database.
* **Task 3.5:** Output the ACR login server URL, database fully qualified domain name (FQDN), and database connection string into an `outputs.tf` file.

### User Story 4: Azure Container Apps Provisioning

**"As an infrastructure administrator, I want to provision serverless Azure Container Apps so that my frontend and backend scale automatically based on traffic."**

* **Task 4.1:** Add an `azurerm_log_analytics_workspace` resource block to `main.tf` for centralizing container logs.
* **Task 4.2:** Add an `azurerm_container_app_environment` resource block linked to the Log Analytics workspace.
* **Task 4.3:** Add an `azurerm_container_app` resource block for the **backend**.
* **Task 4.4:** Configure the backend Container App to pull the image from the ACR, set ingress to external, expose port 8000, and inject the `DATABASE_URL` and `GEMINI_API_KEY` as environment variables securely.
* **Task 4.5:** Add an `azurerm_container_app` resource block for the **frontend**.
* **Task 4.6:** Configure the frontend Container App to pull the Nginx image from ACR, set ingress to external, expose port 80, and inject the backend's FQDN as an environment variable (e.g., `VITE_API_URL`).

### User Story 5: GitHub Actions CI/CD Pipeline (Build & Push)

**"As a developer, I want an automated GitHub Actions workflow to build and push my Docker images whenever code is merged to the main branch."**

* **Task 5.1:** Navigate to GitHub repository settings and configure repository secrets for `AZURE_CREDENTIALS` (Service Principal JSON), `ACR_USERNAME`, `ACR_PASSWORD`, and `TF_API_TOKEN`.
* **Task 5.2:** Create a `.github/workflows/deploy.yml` file.
* **Task 5.3:** Define the pipeline trigger to run `on: push` to the `main` branch.
* **Task 5.4:** Create a `build-and-push` job in the YAML file.
* **Task 5.5:** Add steps to checkout the code, log in to Azure using the `azure/login` action, and log in to the ACR.
* **Task 5.6:** Add a step to run `docker build` using the backend `Dockerfile.prod` and `docker push` it to the ACR, tagging it with the GitHub SHA.
* **Task 5.7:** Add a step to run `docker build` using the frontend `Dockerfile.prod` and `docker push` it to the ACR, tagging it with the GitHub SHA.

### User Story 6: GitHub Actions CI/CD Pipeline (Deploy to Test & Prod)

**"As a developer, I want the pipeline to automatically apply the Terraform configuration to the Test environment, and pause for my manual approval before deploying to Production."**

* **Task 6.1:** Set up two Environments in GitHub Settings: `Test` and `Prod`. Add an explicitly required reviewer for the `Prod` environment.
* **Task 6.2:** Create a `deploy-test` job in `deploy.yml` that `needs: build-and-push` and targets the `Test` GitHub environment.
* **Task 6.3:** Add steps to the `deploy-test` job to setup Terraform (`hashicorp/setup-terraform`), run `terraform init`, and run `terraform apply -auto-approve -var-file="test.tfvars"`.
* **Task 6.4:** Pass the new Docker image tags (GitHub SHA) as variables to the `terraform apply` command so the Container Apps are updated with the newly built images.
* **Task 6.5:** Create a `deploy-prod` job that `needs: deploy-test` and targets the `Prod` GitHub environment.
* **Task 6.6:** Add steps to the `deploy-prod` job to run `terraform init` and `terraform apply -auto-approve -var-file="prod.tfvars"`.

---

This completes the detailed planning phase for your entire application stack, from local development to production deployment!

Would you like me to draft the complete `deploy.yml` GitHub Actions file, or would you prefer to see the `main.tf` structure for the Azure resources?

