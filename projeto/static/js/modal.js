document.addEventListener('DOMContentLoaded', function() {
    var modal = document.getElementById('qrModal');
    var btn = document.querySelector('.nav-botao1');
    var span = document.getElementsByClassName('close')[0];
        
    btn.addEventListener('click', function() {
        modal.style.display = "flex";
        document.body.style.overflow = 'hidden';
    });
        
    span.addEventListener('click', function() {
        modal.style.display = "none";
        document.body.style.overflow = 'auto';
    });
        
    window.addEventListener('click', function(event) {
        if (event.target == modal) {
            modal.style.display = "none";
            document.body.style.overflow = 'auto';
        }
    });
});
