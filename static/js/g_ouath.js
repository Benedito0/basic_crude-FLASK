$('#signinButton').click(function() {
    // signInCallback defined in step 6.
    auth2.grantOfflineAccess().then(signInCallback);
  });

  function signInCallback(authResult) {

  if (authResult['code']) {

    // Hide the sign-in button now that the user is authorized, for example:
    $('#signinButton').attr('style', 'display: none');


    // Send the code to the server
    $.ajax({
      type: 'POST',
      url: '/gconnect?state={{STATE}}',
      // Always include an `X-Requested-With` header in every AJAX request,
      // to protect against CSRF attacks.
      headers: {
        'X-Requested-With': 'XMLHttpRequest'
      },
      contentType: 'application/octet-stream; charset=utf-8',
      data: authResult['code'],
      processData: false,
      success: function(result) {
        if(result)
        {
          $('#result').html('Login successful</br>');
          setTimeout(function()
          {
            window.location.href = "/index";
          }, 3000);


        }else if (authResult['error'])
        {
          console.log("There was an error: " + authResult['error']);
        }
      }
    });
  } else {
    // There was an error.
  }

}