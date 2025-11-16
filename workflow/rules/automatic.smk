"""Rules to used to download automatic resource files."""

rule download_eurostat:
    message:
        "Download stable Eurostat energy balances."
    params:
        url=internal["resources"]["automatic"]["eurostat"],
    output:
        file=temp("resources/automatic/eurostat.zip"),
    log:
        "logs/automatic/download_eurostat.log",
    conda:
        "../envs/shell.yaml"
    shell:
        'curl -sSLo {output.file} "{params.url}"'

rule download_jrc_idees:
    message:
        "Download the JRC IDEES dataset."
    params:
        url=internal["resources"]["automatic"]["jrc_idees"],
    output:
        file=temp("resources/automatic/jrc_idees.zip"),
    log:
        "logs/automatic/download_jrc_idees.log",
    conda:
        "../envs/shell.yaml"
    shell:
        'curl -sSLo {output.file} "{params.url}"'


rule download_hotmaps:
    message:
        "Download the Hotmaps energy intensive industry dataset."
    params:
        url=internal["resources"]["automatic"]["hotmaps"],
    output:
        file="resources/automatic/hotmaps.csv",
    log:
        "logs/automatic/download_hotmaps.log",
    conda:
        "../envs/shell.yaml"
    shell:
        'curl -sSLo {output.file} "{params.url}"'


rule download_ammonia_usgs:
    message:
        "Download the U.S. geological survey on ammonia supply."
    params:
        url=internal["resources"]["automatic"]["ammonia"]["usgs"],
    output:
        file=temp("resources/automatic/ammonia/usgs.xlsx"),
    log:
        "logs/automatic/download_ammonia_usgs.log",
    conda:
        "../envs/shell.yaml"
    shell:
        'curl -sSLo {output.file} "{params.url}"'


rule download_ammonia_plants:
    message:
        "Download ammonia plants as collected by PyPSA-Eur."
    params:
        url=internal["resources"]["automatic"]["ammonia"]["plants"]
    output:
        file="resources/automatic/ammonia/plants.csv",
    log:
        "logs/automatic/download_ammonia_plants.log",
    conda:
        "../envs/shell.yaml"
    shell:
        'curl -sSLo {output.file} "{params.url}"'


rule download_GEM_SPT:
    message:
        "Download the Global Energy Monitor - Steel Plant Tracker."
    params:
        url=internal["resources"]["automatic"]["GEM_SPT"],
    output:
        file="resources/automatic/GEM_SPT.xlsx",
    log:
        "logs/automatic/download_GEM_SPT.log",
    conda:
        "../envs/shell.yaml"
    shell:
        'curl -sSLo {output.file} "{params.url}"'


rule download_cement_non_eu:
    message:
        "Download cement plants as collected by PyPSA-Eur."
    params:
        url=internal["resources"]["automatic"]["non_eu"]["cement"],
    output:
        file="resources/automatic/cement_non_eu.csv",
    log:
        "logs/automatic/download_cement_non_eu.log",
    conda:
        "../envs/shell.yaml"
    shell:
        'curl -sSLo {output.file} "{params.url}"'


rule download_refineries_non_eu:
    message:
        "Download refineries as collected by PyPSA-Eur."
    params:
        url=internal["resources"]["automatic"]["non_eu"]["refineries"],
    output:
        file="resources/automatic/non_eu/refineries.csv",
    log:
        "logs/automatic/download_refineries_non_eu.log",
    conda:
        "../envs/shell.yaml"
    shell:
        'curl -sSLo {output.file} "{params.url}"'


rule download_CHE_industry:
    message:
        "Download CHE industrial production per subsector."
    params:
        url=internal["resources"]["automatic"]["CHE_industry"],
    output:
        file="resources/automatic/CHE_industry.csv",
    log:
        "logs/automatic/download_CHE_industry.log",
    conda:
        "../envs/shell.yaml"
    shell:
        'curl -sSLo {output.file} "{params.url}"'


rule download_GHSL_population:
    message:
        "Download the Global Human Settlement Layer population raster."
    params:
        url=get_ghsl_url(internal["population"]["epoch"], internal["population"]["resolution"]),
    output:
        file=temp("resources/automatic/GHSL.zip"),
    log:
        "logs/automatic/download_CHE_industry.log",
    conda:
        "../envs/shell.yaml"
    shell:
        'curl -sSLo {output.file} "{params.url}"'


rule unzip_directory:
    message:
        "Unzipping {wildcards.directory}."
    input:
        zip_file="resources/automatic/{directory}.zip"
    output:
        directory("resources/automatic/{directory}/")
    wildcard_constraints:
        directory="|".join({"eurostat", "jrc_idees"}),
    log:
        "logs/automatic/unzip_directory_{directory}.log"
    conda:
        "../envs/prepare.yaml"
    script:
        "../scripts/unzip.py"


# TODO: standardised epoch and resolution, or user configured?
rule unzip_GHSL:
    message:
        "Unzipping {params.file}."
    params:
        file=f"GHS_POP_E{internal['population']['epoch']}_GLOBE_R2023A_54009_{internal['population']['resolution']}_V1_0.tif"
    input:
        zip_file="resources/automatic/GHSL.zip"
    output:
        "resources/automatic/GHSL.tif"
    log:
        "logs/automatic/unzip_GHSL.log"
    conda:
        "../envs/prepare.yaml"
    script:
        "../scripts/unzip.py"
