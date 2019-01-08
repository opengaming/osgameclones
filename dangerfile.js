const {danger, markdown} = require('danger')

markdown("Hey there! Thanks for contributing a PR to osgameclones! 🎉")
const modifiedMD = danger.git.modified_files.join("\n- ")
if (modifiedMD.length > 0) {
  markdown("Changed Files in this PR:\n - " + modifiedMD)
}
