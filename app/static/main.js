// Wait for the document to be fully loaded
$(document).ready(function(){
  
  // Listen for clicks on buttons with the class 'btn-primary'
  $('.btn-primary').click(function(){
    
    // Check if the clicked button has a 'data-plan' attribute defined
    if ($(this).data('plan') != undefined) {
        
        // If 'data-plan' attribute is defined, retrieve its value
        let data = $(this).data('plan');
        
        // Set the action attribute of the form inside the paymentModal to '/payment/{data}'
        $('#paymentModal form').attr('action', '/payment/' + data);
    }
  });
});
