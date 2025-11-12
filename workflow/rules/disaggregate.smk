

rule disaggregate_production_key:
    message:
        "Disaggregate industrial production using proxies (population, facilities, emissions)."
    params:
        hotmaps_locate_missing=config["industry"]["hotmaps_locate_missing"],
        countries=config["countries"],
    input:
        regions_onshore="resources/user/shapes_onshore.geojson",
        clustered_pop_layout="resources/user/shapes_population.csv",
        hotmaps=rules.download_hotmaps.output.file,
        gem_gspt=rules.download_GEM_SPT.output.file,
        ammonia=rules.download_ammonia_plants.output.file,
        cement_supplement=rules.download_cement_non_eu.output.file,
        refineries_supplement=rules.download_refineries_non_eu.output.file,
    output:
        industrial_distribution_key="resources/automatic/disaggregate/production_key.csv",
    log:
        "logs/disaggregate/disaggregate_production_key.log",
    conda:
        "../envs/prepare.yaml"
    script:
        "../scripts/disaggregate_production_key.py"
