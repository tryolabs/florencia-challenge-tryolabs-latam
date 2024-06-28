# Chosen model

When deciding between XGBoost and Logistic Regression for the given task, we must consider several critical aspects, including model complexity, performance metrics, handling of non-linearity, interpretability, and scalability. Below is a more in-depth comparison and justification for choosing XGBoost over Logistic Regression.

1. Handling of non-linearity:

* XGBoost:
XGBoost is a powerful ensemble learning method based on decision trees. It excels at capturing non-linear relationships and interactions between features without requiring explicit feature engineering.
The model can handle complex patterns in data, making it more flexible and capable of achieving higher performance on diverse datasets.

* Logistic Regression:
Logistic Regression is a linear model that assumes a linear relationship between the input features and the log-odds of the outcome. It may not perform well when the relationship between features and the target variable is non-linear or involves interactions between features.
To handle non-linear relationships, additional feature engineering is needed, which can increase model complexity and reduce interpretability.

2. Performance metrics:

* Both models show similar performance metrics, but XGBoost often performs better in real-world scenarios due to its ability to handle more complex patterns.
Moreover, XGBoost has a higher F1-score for the positive class, which is the one representing the delays. F1-score merges precision and recall into one metric, balancing both false positives and false negatives.

3. Feature importance and interpretability:

* XGBoost:
XGBoost provides a built-in mechanism for feature importance, making it easier to interpret which features contribute the most to the model's predictions.
While it is generally less interpretable than linear models due to its complexity, the feature importance scores help understand the model.

* Logistic Regression:
Logistic Regression offers straightforward interpretability through its coefficients.

4. Scalability and efficiency:

* XGBoost:
XGBoost is highly optimized for efficiency and scalability. It supports parallel processing and can handle large datasets efficiently.
It includes regularization terms to prevent overfitting, making it robust for high-dimensional data.

* Logistic Regression:
Logistic Regression is computationally less intensive and scales well with large datasets. However, it might struggle with high-dimensional data where feature interactions are crucial.

**Conclusion:**
I chose XGBoost with feature importance and balance as the best model due to its superior capability in handling non-linearity and interactions and robust performance metrics. While Logistic Regression is simpler and more interpretable, it might fall short in capturing complex patterns and interactions in the data, which are crucial for predicting flight delays accurately.

> **_NOTE_ :** The instructions said specifically not to modify the model, but I would make changes on the features selected (for instance not hardcoding them).

# API

I used Enums to handle validations in the data. I could have used the pydantic validators but I felt this approach was more clean and pythonic. 

Also, I added code to the preprocess step in the model to handle unseen classes in training. 

## IaC: Terraform

I decided to use Terraform for the infrastructure. Using Terraform for managing cloud infrastructure offers significant advantages, particularly in the realms of automation, consistency, and scalability. As an Infrastructure as Code (IaC) tool, it allows developers and operations teams to define and provision all infrastructure resources using declarative configuration files. This ensures that environments can be replicated across different stages of the development lifecycle, reducing the risk of configuration drift and manual errors. Moreover, Terraform's state management and planning capabilities provide clear visibility into the changes that will be applied, facilitating better collaboration and change management. By automating the deployment of resources, Terraform not only accelerates the provisioning process but also enhances reliability and reduces operational overhead. What is more, its cloud-agnostic nature allows teams to manage resources across multiple cloud providers and on-premises environments with a consistent workflow.

It's important to note that the approach I used here is not the most organized. Typically, I would maintain all infrastructure code in a separate repository and create multiple Terraform environments to manage resources for each environment. Additionally, a better practice would be to have a "common" environment to create shared resources like the artifact registry, which are needed beforehand. For this example, I had to create the artifact registry using the command line because I needed it to push the Docker image. Only after pushing the image could I apply the Terraform configuration to deploy the rest of the infrastructure.

### How would I maintain different environments with terraform? I would create generic modules for the resources that can be instantiated once per environment with their own values for each variable. Everything could be parameterized and tagged by environment. In this way the infrastructure and MLOps workflows can be tidy, separated between environments and extensible. 

Commands: After authenticating, setting the project ID and enabling the APIs.

Create artifact registry: 
```
gcloud artifacts repositories create florencia-repo-latam-challenge --repository-format=docker --location=us --description="Docker repository"
```
Build docker image: 
```
docker build -t us-docker.pkg.dev/florencia-tryolabs-latam/florencia-repo-latam-challenge/latam-challenge:latest .
```
Push image to artifact registry: 
```
docker push us-docker.pkg.dev/florencia-tryolabs-latam/florencia-repo-latam-challenge/latam-challenge:latest
``` 
Initialize Terraform: 
```
terraform init
```
See changes on resources: 
```
terraform plan
```
Apply changes on the infrastructure: 
```
terraform apply
```

<mark>IMPORTANT:</mark> For simplicity, I didn't handle secrets such as the project name and image URL in the most optimal way. Due to time constraints and the fact that this is a test, I chose not to impose rigid constraints. In a real-world scenario, I would utilize a secrets manager in Google for securely managing these secrets and injecting them to the container created. For the secrets in Terraform I could read them from a local env file or even have them in GitHub actions. Additionally, for simplicity, I granted public access to the API, making the service accessible to anyone on the internet. However, in a real-world scenario, a proper policy with appropriate permissions would be implemented to secure the API access.

> **_NOTE ON IMPROVING EFFICIENCY_ 📈:**
To improve efficiency, I created a .dockerignore file to exclude the environment files, resulting in a smaller image. Additionally, I moved the pip install instruction to occur before copying the code in the Dockerfile. This takes advantage of layer caching, so when the image is rebuilt due to code changes, it doesn't need to reinstall all the dependencies, reducing build time.

# CI/CD

As the models folder is in the gitignore, it is not uploaded to the repository and therefore not available in the docker image build inside the workflow environment. In order to run the stress tests I need to have a model available. As a temporary solution I decided to create a bucket in GCP to store the trained model so that it could be retrieved during the workflow. Of course in a  real-world scenario I would never use the model trained in development for production and I wouldn’t also have a public bucket with no restrictions in permissions. This flow could improve exponentially if we had a model registry and good version control of models, with independent training jobs that upload to that registry and a proper handling to download those models and deploy them in the API.

There is no one perfect way to do CI/CD. I decided to execute the CI workflow on every pull request made to develop and the CD on every pull request made to main. However, it's important to note that in reality most of the times these two stages (CI and CD) are often merged into one. 
What is more, in this particular case we are not managing a staging or integration environment but it is of paramount importance to have one before getting changes on production. 

# Errors fixed to run the notebook:

* When faced with the error: “barplot() takes from 0 to 1 positional arguments but 2 were given.” I added x=.. and y=... to the barplots definition. 

* The variable training_data was defined but never used, so I didn’t use it in the model’s definition. 

* I added xgboost to the requirements file since it was not included.

* I changed () for [] in the return type of the preprocess function. 

* The function is_high_season has a bug since it doesn’t consider the time.


* I changed the data path in the test_model.py file.
