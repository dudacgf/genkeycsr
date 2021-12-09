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

function copy_contents(input_field) {
   var copyText = document.getElementById(input_field);

   if (copyText.innerHTML.trim() == '') {
      $('#show_error').html('<span class="warning small tw-bold">Please, generate key/csr pair before copying to clipboard.</span>');
      setTimeout(function() { 
         $('#show_error').html('');
     }, 3000);
     return;
   }
 
   navigator.clipboard.writeText(copyText.innerHTML);
 
   /* Alert the copied text */
   $('#show_error').html('<span class="info small tw-bold">text copied to clipboard</span>');

   setTimeout(function() { 
       $('#show_error').html('');
   }, 3000);

 } 

function download_contents(input_field, extension) {
   var copyText = document.getElementById(input_field);

   if (copyText.innerHTML.trim() == '') {
      $('#show_error').html('<span class="warning small tw-bold">Please, generate key/csr pair before downloading.</span>');
      setTimeout(function() { 
         $('#show_error').html('');
     }, 3000);
     return;
   }
 
   var base64_contents = btoa(unescape(encodeURIComponent(copyText.innerHTML))),
          a = document.createElement('a'),
          e = new MouseEvent('click');
    
   var common_name = document.getElementById('common_name').value;

   a.download = common_name + '.' + extension;
   a.href = 'data:text/text;base64,' + base64_contents;
   a.dispatchEvent(e);
}