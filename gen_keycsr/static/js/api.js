/* calls route to generate pair. 
   response will be a json object containing
   status: 'error' 'success'
   messages: any flashed messages triggered during processing
   key: private rsa key in pem format
   csr: private certificate signing request in pem format
*/
function generate_key_csr_pair() {
   var form_data = new FormData();
   
   $("form :input").each(function(){
      var field_value = $(this).val();//the value of the current input element
      var field_name = $(this).attr('name');//input name
      form_data.append(field_name, field_value);
  });

   $.ajax({
       url: '/generate_key_csr_pair',
       cache: false,
       contentType: false,
       processData: false,
       data: form_data,
       type: 'post',
       success: function (response) {
          if (response.status == 'success') {
             var key = response.key.replace('\n', '\n\r')
             var csr = response.csr.replace('\n', '\n\r')
             $('#show_key').html(key)
             $('#show_csr').html(csr)
          } else if (response.status == 'error') {
             $('#show_error').html(response.messages)
          }
       },
       error: function (response) {
           console.log('error')
       }
   });

   setTimeout(function() { 
       $('#show_error').html('');
   }, 3000);

   return;
}