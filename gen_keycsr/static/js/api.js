/* calls route to generate pair. 
   response will be a json object containing
   status: 'error' 'success'
   messages: any messages triggered during processing
   key: private rsa key in pem format
   csr: private certificate signing request in pem format
*/
function generate_pair() {
   var form_data = new FormData();
   
   $("form :input").each(function(){
      var field_value = $(this).val();//the value of the current input element
      var field_name = $(this).attr('name');//input name
      form_data.append(field_name, field_value);
  });

   /* corrects value of self_signed field. If I used $(this).val(), it would be always 'y' (and I don't know why) */
   var self_signed = document.getElementById('self_signed');
   form_data.set('self_signed', self_signed.checked); 

   $.ajax({
       url: '/generate_pair',
       cache: false,
       contentType: false,
       processData: false,
       data: form_data,
       type: 'post',
       success: function (response) {
          if (response.status == 'success') {
             $('#show_key').html(response.key)
             $('#show_cert').html(response.cert)
          } else if (response.status == 'error') {
             pop_message(response.messages)
          }
       },
       error: function (response) {
           console.log('error')
       }
   });

   return;
}

/* copy the innerHTML of an element to the clipboard
   receives the name of the element
   flashes successfuss message
*/
function copy_contents(input_field) {
   var copyText = document.getElementById(input_field);

   if (copyText.innerHTML.trim() == '') {
      pop_message('<h2>Copy to clipboard:</h2><span class="small">Please, generate key/csr pair before copying to clipboard.<span>');
      return;
   }

   try{
      navigator.clipboard.writeText(copyText.innerHTML);
   }
   catch (error) {
      pop_message('<h2>Error copying to clipboard ' + error + '</h2>');
      return;
   }

   /* Alert the copied text */
   pop_message('<h2>text copied to clipboard</h2>');

} 

/* Offers the innertHTML contents of an element as a text/text download
   receives the id of the element and the name of the extension to be used
*/
function download_contents(input_field, field) {
   var copyText = document.getElementById(input_field);

   if (copyText.innerHTML.trim() == '') {
      pop_message('<h2>Download:</h2><span class="small">Please, generate key/csr pair before downloading.<span>');
      return;
   }
 
   var base64_contents = btoa(copyText.innerHTML);
   var a = document.createElement('a');
   var  e = new MouseEvent('click');
    
   var common_name = document.getElementById('common_name').value;
   if (field == 'cert') {
      var extension = document.getElementById('cert_title').textContent.toLowerCase();
   } else {
      var extension = 'key';
   }

   a.download = common_name + '.' + extension;
   a.href = 'data:text/text;base64,' + base64_contents;
   a.dispatchEvent(e);
}

/* just pops a message using a field that gets visible when not empty
   receives: message to be poped
*/
function pop_message(message) {
   $('#show_message').html(message);
   setTimeout(function() { 
      $('#show_message').html('');
   }, 3000);
   return;
}

/* Changes the title of the certificate result region (CSR<->CRT) when self_signed checkbox is clicked */
function change_csr_crt_div_title() {
   var self_signed = document.getElementById('self_signed');
   var cert_title = document.getElementById('cert_title')

   if (self_signed.checked) {
      cert_title.textContent = 'CRT ';
   } else {
      cert_title.textContent = 'CSR ';
   }
}