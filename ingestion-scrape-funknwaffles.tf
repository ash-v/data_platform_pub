module "scrape_funknwaffles" {
    source = "./modules/data_ingestion/scrapper_funknwaffles/"   
    lambda_function_name = "scrape-funknwaffles-to-rawzone"
}

