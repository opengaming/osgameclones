const {danger, message} = require('danger')

message('Files in change set:', danger.git.modified_files);
