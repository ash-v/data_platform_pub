module "download_images" {
    source = "./modules/data_processing/download_images/"   
    lambda_function_name = "download-images"
}

