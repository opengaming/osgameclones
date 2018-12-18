const {danger, markdown} = require('danger')

const modifiedMD = danger.git.modified_files.join("\n- ")
markdown("Changed Files in this PR:\n - " + modifiedMD)
