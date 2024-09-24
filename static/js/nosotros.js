$(document).ready(function() {
    // Configuración del carrusel
    $('.carousel').slick({
        autoplay: true,
        autoplaySpeed: 2000,
        dots: true,
        arrows: false,
        fade: true
    });

    // Efectos de animación para las secciones
    const revealSection = function() {
        $('.section-content, .mision, .vision, .valores-content, .team').each(function() {
            const windowHeight = $(window).height();
            const elementTop = $(this).offset().top;
            const scrollTop = $(window).scrollTop();
            
            if (scrollTop + windowHeight > elementTop + 100) {
                $(this).addClass('reveal');
            }
        });
    };

    // Activar el efecto de revelar secciones al hacer scroll
    $(window).on('scroll', function() {
        revealSection();
    });

    // Llamar a la función al cargar la página
    revealSection();
});
