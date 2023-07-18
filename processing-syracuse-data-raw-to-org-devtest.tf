module "process_syracuse_data_devtest" {
    source = "./modules/data_processing/process_syracuse_data_devtest/"   
    lambda_function_name = "process-syracuse-data-raw-to-orgzone-devtest"
}