module "scrape_eversonmuseum" {
    source = "./modules/data_ingestion/scrapper_eversonmuseum/"   
    lambda_function_name = "scrape-eversonmuseum-to-rawzone"
}

