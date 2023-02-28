SET(PROP_APPS
  parMaker 
)


foreach(appname ${PROP_APPS})
  cet_make_exec(NAME ${appname}
    SOURCE 
      ${appname}.cc
    LIBRARIES PRIVATE
    geant4reweight::PropBaseLib
    ROOT::RIO
    fhiclcpp::fhiclcpp
  )

endforeach()
