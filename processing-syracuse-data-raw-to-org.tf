module "process_syracuse_data" {
    source = "./modules/data_processing/process_syracuse_data/"   
    lambda_function_name = "process-syracuse-data-raw-to-orgzone"
}

