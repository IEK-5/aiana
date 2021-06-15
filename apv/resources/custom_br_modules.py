import bifacial_radiance as br

# Making module with all the variables
pv_module_sunFarming = br.RadianceObj.makeModule(
    name=moduletype,
    x=x,
    y=y,
    numpanels=numpanels,
    xgap=xgap,
    ygap=ygap,
    cellLevelModuleParams={
        'numcellsx': 6,
        'numcellsy': 12,
        'xcell': 0.156,
        'ycell': 0.156,
        'xcellgap': 0.02,
        'ycellgap': 0.02
    })
