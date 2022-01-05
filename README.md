# MLOps on Azure

This is a MLOps pipeline to train and deploy an ALBERT model on Azure (MLOps maturity level 3).

![image001 (3)](https://user-images.githubusercontent.com/81354022/148173706-cc22d53c-b025-471a-9048-9f04400215c2.jpg)

## Steps (Training):
1) The pipeline will be triggered by a) Azure Logic Apps which detected a change in the Blob Storage holding the data or b) a commit to the repository (either GitHub or Azure Repos)
2) Either the Azure CLI or a Terraform script could be used to provision the resources needed (The resource group, Azure Machine Learning workspace, compute cluster)
3) Azure Machine Learning will automatically train the ALBERT model using data in the /data folder or in Azure Blob Storage, depending on where the data is stored
4) ALBERT model will be converted into ONNX format and registered in the AML workspace

## Steps (Deployment) 
5a) The ONNX model can be deployed to Azure Container Instances as an endpoint (REST API) --usually for pre-production and testing

OR

5b) The ONNX model can be deployed to Azure Kubernetes Services as an endpoint (REST API) --usually for production

The endpoint can now be called by a user, and the model performance will be monitored on Azure Machine Learning.
