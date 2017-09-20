(function($, window, document, undefined) {
	var $win = $(window);
	var $doc = $(document);

	$doc.ready(function() {
		// Tabs
		$('.tabs__nav a').on('click', function(event) {
			event.preventDefault();

			var $this = $(this);
			var src = $this.attr('href');
			var $listItem = $this.closest('li');
			var currentClass = 'current';
			var hoverClass = 'hover';

			$('.tabs__nav a').removeClass(hoverClass);
			$this.addClass(hoverClass);

			$listItem
				.add($(src))
				.addClass(currentClass)
				.siblings()
				.removeClass(currentClass);
		});

		//Mobile navigation show/hide
		$('.burger').on('click', function(event) {
			$(this).toggleClass('burger--active');
			$('.nav').toggleClass('nav--visible');
				
			event.preventDefault();
		});
	});
})(jQuery, window, document);
