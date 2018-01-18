Dropzone.autoDiscover = false;
$(function() {

  var myDropzone = new Dropzone(
    '#dropzone-upload',
  {
    uploadMultiple: true,
    addRemoveLinks: true,
    maxFiles: 150,
    dictDefaultMessage: '',
    autoProcessQueue: false,
    previewsContainer: '.upload-files .row',
    dictRemoveFile: '',
    previewTemplate: `
    <div class="col-sm-2">
      <figure class="upload-files__image">
        <img data-dz-thumbnail>

        <a href="#">
          <i class="ico-delete" data-dz-remove></i>
        </a>

        <div class="caption">
          <p data-dz-name>default name</p>

          <p><span data-dz-size>default size</span></p>
        </div><!-- /.caption -->
      </figure><!-- /.upload-files__image -->
    </div><!-- /.col-sm-2 -->
    <div data-dz-uploadprogress></div>
    <div data-dz-errormessage></div>
    `,
    success: function(file, response) {
      window.location = response['redirect_url']
    }
  })

  $('.process_queue').on('click', function(){
    myDropzone.processQueue();
  })
  $('.browse').on('click', function(e){
    $('.dz-message').click();
  })
})

