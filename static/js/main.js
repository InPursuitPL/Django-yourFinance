function main() {
	$('.imgLinks').hide();
	$('.imgLinks').fadeIn(2000);
	$('#configureLinks').hide();
	$('.configureButton').on('click', function() {
		$('#configureLinks').toggle();
		$('.configureButton').toggleClass('active');
	})
};

$(document).ready(main);
