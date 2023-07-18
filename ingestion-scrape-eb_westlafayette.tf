module "scrape_eb_westlafayette" {
    source = "./modules/data_ingestion/scrapper_eb_westlafayette/"   
    lambda_function_name = "scrape-eb-westlafayette-to-rawzone"
} 

