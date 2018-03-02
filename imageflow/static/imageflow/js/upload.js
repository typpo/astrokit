Dropzone.autoDiscover = false;
$(function() {

  var redirectUrl = null;
  var myDropzone = new Dropzone(
    '#dropzone-upload',
  {
    uploadMultiple: true,
    addRemoveLinks: true,
    maxFiles: 150,
    // TODO(ian): Limit the number of parallel uploads. Dropzone will make a
    // new upload request for each upload, so we need to figure out how to put
    // ALL the uploads into a single light curve.
    parallelUploads: 150,
    dictDefaultMessage: '',
    autoProcessQueue: false,
    previewsContainer: '.upload-files .row',
    dictRemoveFile: '',
    previewTemplate: `
    <div class="col-sm-12">
      <span data-dz-name>default name</span>
      <span data-dz-size>default size</span>
    </div><!-- /.col-sm-12 -->
    <div data-dz-uploadprogress></div>
    <div data-dz-errormessage></div>
    `,
    /*
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
    */
      success: function(file, response) {
      redirectUrl = response['redirect_url']
    },
    init: function() {
      // TODO(ian): Disable the upload button.
      this.on('queuecomplete', function () {
        // this.options.autoProcessQueue = false;
        if (!redirectUrl) {
          alert('Something went wrong and we cannot redirect to your light curve :(');
          return;
        }
        window.location = redirectUrl;
      });
      this.on('processing', function() {
        this.options.autoProcessQueue = true;
      });
    },
  });

  $('.process_queue').on('click', function(){
    myDropzone.processQueue();
  })
  $('.browse').on('click', function(e){
    $('.dz-message').click();
  })
})

