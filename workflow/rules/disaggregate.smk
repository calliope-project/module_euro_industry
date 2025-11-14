

rule disaggregate_production_key:
    message:
        "Disaggregate industrial production using proxies (population, facilities, emissions)."
    params:
        hotmaps_locate_missing=config["industry"]["hotmaps_locate_missing"],
        countries=config["countries"],
        geographic_crs=internal["crs"]["geographic"]
    input:
        regions_onshore=rules.prepare_shapes.output.filtered,
        hotmaps=rules.download_hotmaps.output.file,
        gem_gspt=rules.download_GEM_SPT.output.file,
        ammonia=rules.download_ammonia_plants.output.file,
        cement_supplement=rules.download_cement_non_eu.output.file,
        refineries_supplement=rules.download_refineries_non_eu.output.file,
    output:
        industrial_distribution_key="resources/automatic/shapes/{shape}/disaggregated_production_key.csv",
    log:
        "logs/disaggregate/disaggregate_{shape}_production_key.log",
    conda:
        "../envs/prepare.yaml"
    script:
        "../scripts/disaggregate_production_key.py"


rule disaggregate_current_industrial_energy_demand:
    input:
        industrial_distribution_key=rules.disaggregate_production_key.output.industrial_distribution_key,
        industrial_energy_demand_per_country_today=rules.prepare_current_energy_demand_per_country.output.current_energy_demand,
    output:
        industrial_energy_demand_per_node_today="results/disaggregated/current_industrial_energy_demand.csv",
    log:
        "logs/disaggregated/disaggregate_current_industrial_energy_demand.log",
    conda:
        "../envs/prepare.yaml"
    script:
        "../scripts/disaggregate_current_industrial_energy_demand.py"


rule disaggregate_future_industrial_production:
    input:
        industrial_distribution_key=rules.disaggregate_production_key.output.industrial_distribution_key,
        industrial_production_per_country_tomorrow="results/aggregated/future_production_{year}.csv",
    output:
        industrial_production_per_node="results/disaggregated/future_production_{year}.csv",
    log:
        "logs/disaggregate/disaggregate_future_industrial_production_{year}.log",
    conda:
        "../envs/prepare.yaml"
    script:
        "../scripts/disaggregate_future_industrial_production.py"


rule disaggregate_future_industrial_energy_demand:
    input:
        industry_sector_ratios=rules.prepare_sector_ratios_intermediate.output.industry_sector_ratios,
        industrial_production_per_node="results/disaggregated/future_production_{year}.csv",
        industrial_energy_demand_per_node_today="results/disaggregated/current_industrial_energy_demand.csv",
    output:
        industrial_energy_demand_per_node="results/disaggregated/future_energy_demand_{year}.csv",
    log:
        "logs/disaggregate/disaggregate_future_industrial_energy_demand_{year}.log",
    conda:
        "../envs/prepare.yaml"
    script:
        "../scripts/disaggregate_future_industrial_energy_demand.py"
