const {danger, info} = require('danger')

info('Files in change set:', danger.git.modified_files);
