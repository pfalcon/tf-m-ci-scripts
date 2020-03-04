//-------------------------------------------------------------------------------
// Copyright (c) 2020, Arm Limited and Contributors. All rights reserved.
//
// SPDX-License-Identifier: BSD-3-Clause
//
//-------------------------------------------------------------------------------

package org.trustedfirmware;

@NonCPS
def getBuildCsv(results) {
  def table = [:]
  def projects = []
  results.each { result ->
    res = result.value[0]
    config = result.value[1]
    params = result.value[2]
    if (params['BL2'] == 'True') {
      bl2_string = 'BL2'
    } else {
      bl2_string = 'NOBL2'
    }
    if (params["PSA_API_SUITE"].isEmpty()) {
      psa_string = ""
    } else {
      psa_string = "_${params['PSA_API_SUITE']}"
    }
    row_string = "${params['TARGET_PLATFORM']}_${params['COMPILER']}_${params['CMAKE_BUILD_TYPE']}_${bl2_string}${psa_string}"
    column_string = "${params['PROJ_CONFIG']}"
    row = table[row_string]
    if (row == null) {
      row = [:]
    }
    row[column_string] = res.getResult()
    table[row_string] = row
    if(!projects.contains(params['PROJ_CONFIG'])) {
      projects += params['PROJ_CONFIG']
    }
  }
  header = []
  header += "" // top left
  header.addAll(projects)
  header.sort { it.toLowerCase() }
  csvContent = []
  for (row in table) {
    row_item = []
    row_item += row.key
    for (project in projects) {
      result = table[row.key][project]
      if (result == null) {
        result = "N/A"
      }
      row_item += result
    }
    csvContent.add(row_item)
  }
  csvContent.sort { it[0].toLowerCase() }
  csvContent.add(0, header)
  return csvContent
}

@NonCPS
def getLinks(results) {
  linksContent = []
  results.each { result ->
    res = result.value[0]
    config = result.value[1]
    url = res.getAbsoluteUrl()
    linksContent.add("${config}: <a href=\"${url}\">Job</a>/<a href=\"${url}/artifact/build.log/*view*/\">Logs</a>/<a href=\"${url}/artifact/\">Artifacts</a><br/>")
  }
  linksContent.sort()
  return linksContent.join("\n")
}
