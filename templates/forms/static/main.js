function submitForm() {
  var $form = $("form");
  if (validate($form)) {
    // https://github.com/marioizquierdo/jquery.serializeJSON
    var data = $form.serializeJSON({
      customTypes: {
        csv: function(str) {
          if (str === "") {
            return null;
          }
          return $.csv.toArray(str);
        },
      }
    });
    // Remove empty nodes
    data = trimObject(data);
    var dumped = jsyaml.safeDump(data, {
      noArrayIndent: true,
    });
    console.log(dumped);
    $('#add-game-yaml-body').val(dumped);
    $('#yaml-modal').modal();
    return false;
  } else {
    // Form is invalid; let the browser's built in validation show
    return true;
  }
}

function validate($form) {
  // Check required for multiple checkboxes
  var valid = true;
  $form.find('.checkbox-group-required').each(function(i, elem) {
    $(elem).find(':checkbox').removeAttr('required');
    if ($(elem).find(':checkbox:checked').length === 0) {
      // Set one of them to required to use the browser's own validation message
      $(elem).find(':checkbox').attr('required', 'required');
      valid = false;
    }
  });
  valid = valid && $form.get()[0].checkValidity();
  return valid;
}

function trimObject(o) {
  if (typeof o === 'object') {
    for (var a in o) {
      o[a] = trimObject(o[a]);
      if (!o[a] || (o[a].constructor === Object && Object.keys(o[a]).length === 0)) {
        delete o[a];
      }
    }
  } else if (Array.isArray(o)) {
    o = o.map(function(e) {
      return trimObject(e);
    });
  }
  return o;
}

function copy() {
  $("#add-game-yaml-body").select();
  document.execCommand("copy");
}

$("input.tagsinput").each(function() {
  $(this).tagsinput({
    allowDuplicates: this.hasAttribute("data-allow-duplicates")
  });
});

$("input.datepicker").datepicker({
  format: "yyyy-mm-dd",
  autoclose: true,
  todayBtn: "linked",
  todayHighlight: true
});
