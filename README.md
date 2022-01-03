# MLOps on Azure

This is a MLOps pipeline to train and deploy an ALBERT model on Azure (MLOps maturity level 3).

![image005 (1)](https://user-images.githubusercontent.com/81354022/147899076-8a406133-e338-47f5-b278-2aea2347a2d1.jpg)

## Steps (Training):
1) A code commit to the repository (either GitHub or Azure Repos) will trigger the pipeline
2) Either the Azure CLI or a Terraform script could be used to provision the resources needed (The resource group, Azure Machine Learning workspace, compute cluster)
3) Azure Machine Learning will automatically train the ALBERT model using data in the /data folder
4) ALBERT model will be converted into ONNX format and registered in the AML workspace

## Steps (Deployment) 
5a) The ONNX model can be deployed to Azure Container Instances as an endpoint (REST API) --usually for pre-production and testing

OR

5b) The ONNX model can be deployed to Azure Kubernetes Services as an endpoint (REST API) --usually for production

The endpoint can now be called by a user, and the model performance will be monitored on Azure Machine Learning.
