rule build_food_beverages_tobacco_ratios:
    message: "building the food,beverages, and tobacco sector ratio for {wildcards.year}"
    input:
        idees_path = "resources/automatic/jrc_idees/",
    params:
        reference_year = config["industry"]["reference_year"],
        sector_config = config["sectors"]["food_beverages_tobacco"]
    output:
        file = "resources/automatic/build/food_beverages_tobacco_ratio_{year}.csv"
    log:
        "logs/build/build_food_beverages_tobacco_ratios_{year}.log",
    script:
        "../scripts/build_food_beverages_tobacco_ratios.py"


rule build_iron_and_steel_ratios:
    message: "building the Iron and Steel sector ratio for {wildcards.year}"
    input:
        idees_path = "resources/automatic/jrc_idees/",
    params:
        reference_year = config["industry"]["reference_year"],
        sector_config = config["sectors"]["iron_and_steel"]["production_routes"]
    output:
        file = "resources/automatic/build/iron_and_steel_ratio_{year}.csv"
    log:
        "logs/build/build_iron_and_steel_ratios_{year}.log",
    script:
        "../scripts/build_iron_and_steel_ratios.py"


rule transport_equipment_ratios:
    message: "building the Transport Equipment sector ratio for {wildcards.year}"
    input:
        idees_path = "resources/automatic/jrc_idees/",
    params:
        reference_year = config["industry"]["reference_year"],
        sector_config = config["sectors"]["transport_equipment"]
    output:
        file = "resources/automatic/build/transport_equipment_ratio_{year}.csv"
    log:
        "logs/build/transport_equipment_ratios_{year}.log",
    script:
        "../scripts/build_transport_equipment_ratios.py"


rule machinery_equipment_ratios:
    message: "building the Machinery Equipment sector ratio for {wildcards.year}"
    input:
        idees_path = "resources/automatic/jrc_idees/",
    params:
        reference_year = config["industry"]["reference_year"],
        sector_config = config["sectors"]["machinery_equipment"]
    output:
        file = "resources/automatic/build/machinery_equipment_ratio_{year}.csv"
    log:
        "logs/build/machinery_equipment_ratios_{year}.log",
    script:
        "../scripts/build_machinery_equipment_ratios.py"


rule textiles_and_leather_ratios:
    message: "building the textiles and leather sector ratio for {wildcards.year}"
    input:
        idees_path = "resources/automatic/jrc_idees/",
    params:
        reference_year = config["industry"]["reference_year"],
        sector_config = config["sectors"]["textiles_and_leather"]
    output:
        file = "resources/automatic/build/textiles_and_leather_ratio_{year}.csv"
    log:
        "logs/build/textiles_and_leather_ratios_{year}.log",
    script:
        "../scripts/build_textiles_and_leather_ratios.py"


rule wood_and_wood_products_ratios:
    message: "building the wood and wood products sector ratio for {wildcards.year}"
    input:
        idees_path = "resources/automatic/jrc_idees/",
    params:
        reference_year = config["industry"]["reference_year"],
        sector_config = config["sectors"]["wood_and_wood_products"]
    output:
        file = "resources/automatic/build/wood_and_wood_products_ratio_{year}.csv"
    log:
        "logs/build/wood_and_wood_products_ratios_{year}.log",
    script:
        "../scripts/build_wood_and_wood_products_ratios.py"

rule other_industrial_sectors_ratios:
    message: "building the other industrial sectors ratio for {wildcards.year}"
    input:
        idees_path = "resources/automatic/jrc_idees/",
    params:
        reference_year = config["industry"]["reference_year"],
        sector_config = config["sectors"]["other_industrial_sectors"]
    output:
        file = "resources/automatic/build/other_industrial_sectors_ratio_{year}.csv"
    log:
        "logs/build_other_industrial_sectors_{year}.log",
    script:
        "../scripts/build_other_industrial_sectors_ratios.py"


rule pulp_paper_printing_ratios:
    message: "building the pulp, paper, and printing sectors ratio for {wildcards.year}"
    input:
        idees_path = "resources/automatic/jrc_idees/",
    params:
        reference_year = config["industry"]["reference_year"],
        sector_config = config["sectors"]["pulp_paper_printing"]
    output:
        file = "resources/automatic/build/pulp_paper_printing_ratio_{year}.csv"
    log:
        "logs/build_pulp_paper_printing_{year}.log",
    script:
        "../scripts/build_pulp_paper_printing_ratios.py"


rule build_aluminium_ratios:
    message: "building the Aluminium production ratio for {wildcards.year}"
    input:
        idees_path = "resources/automatic/jrc_idees/",
    params:
        reference_year = config["industry"]["reference_year"],
        sector_config = config["sectors"]["aluminium"]["production_routes"]
    output:
        file = "resources/automatic/build/aluminium_ratio_{year}.csv"
    log:
        "logs/build/build_aluminium_ratios_{year}.log",
    script:
        "../scripts/build_aluminium_ratios.py"



rule non_ferrous_metals_ratios:
    message: "building the non ferrous metals sectors (excluding aluminium) ratio for {wildcards.year}"
    input:
        idees_path = "resources/automatic/jrc_idees/",
    params:
        reference_year = config["industry"]["reference_year"],
        sector_config = config["sectors"]["non_ferrous_metals"]
    output:
        file = "resources/automatic/build/non_ferrous_metals_ratio_{year}.csv"
    log:
        "logs/build_non_ferrous_metals_{year}.log",
    script:
        "../scripts/build_non_ferrous_metals_ratios.py"

rule cement_ratios:
    message: "building the cement ratio for {wildcards.year}"
    input:
        idees_path = "resources/automatic/jrc_idees/",
    params:
        reference_year = config["industry"]["reference_year"],
        sector_config = config["sectors"]["cement"]["production_routes"]
    output:
        file = "resources/automatic/build/cement_ratio_{year}.csv"
    log:
        "logs/build_cement_{year}.log",
    script:
        "../scripts/build_cement_ratios.py"   


rule ceramics_ratios:
    message: "building the ceramics ratio for {wildcards.year}"
    input:
        idees_path = "resources/automatic/jrc_idees/",
    params:
        reference_year = config["industry"]["reference_year"],
        sector_config = config["sectors"]["ceramics"]["production_routes"]
    output:
        file = "resources/automatic/build/ceramics_ratio_{year}.csv"
    log:
        "logs/build_ceramics_{year}.log",
    script:
        "../scripts/build_ceramics_ratios.py"  

rule glass_ratios:
    message: "building the glass ratio for {wildcards.year}"
    input:
        idees_path = "resources/automatic/jrc_idees/",
    params:
        reference_year = config["industry"]["reference_year"],
        sector_config = config["sectors"]["glass"]["production_routes"]
    output:
        file = "resources/automatic/build/glass_ratio_{year}.csv"
    log:
        "logs/build_glass_{year}.log",
    script:
        "../scripts/build_glass_ratios.py"  

rule build_high_value_chemicals_ratios:
    message: "building the High Value Chemical sector ratio for {wildcards.year}"
    input:
        idees_path = "resources/automatic/jrc_idees/",
        ammonia_production = rules.prepare_ammonia_production.output.prepared,
    params:
        reference_year = config["industry"]["reference_year"],
        sector_config = config["sectors"]["high_value_chemicals"]["production_routes"],
        extra_data = config["industry"],
    output:
        file = "resources/automatic/build/high_value_chemicals_ratio_{year}.csv"
    log:
        "logs/build/build_high_value_chemicals_ratios_{year}.log",
    script:
        "../scripts/build_high_value_chemicals_ratio.py"

rule build_other_chemicals_ratio:
    message: "building the other chemicals sectors ratio for {wildcards.year}"
    input:
        idees_path = "resources/automatic/jrc_idees/",
    params:
        reference_year = config["industry"]["reference_year"],
        sector_config = config["sectors"]["pulp_paper_printing"]
    output:
        file = "resources/automatic/build/other_chemicals_ratio_{year}.csv"
    log:
        "logs/build_other_chemicals_{year}.log",
    script:
        "../scripts/build_other_chemicals_ratios.py"


rule build_pharmaceutical_products_ratio:
    message: "building the pharmaceutical products sectors ratio for {wildcards.year}"
    input:
        idees_path = "resources/automatic/jrc_idees/",
    params:
        reference_year = config["industry"]["reference_year"],
        sector_config = config["sectors"]["pulp_paper_printing"]
    output:
        file = "resources/automatic/build/pharmaceutical_products_ratio_{year}.csv"
    log:
        "logs/build_pharmaceutical_products_{year}.log",
    script:
        "../scripts/build_pharmaceutical_products_ratios.py"