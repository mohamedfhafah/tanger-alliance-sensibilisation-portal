// Système de notation dynamique par étoiles pour la page de détail simulation uniquement

const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;

document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.star-rating').forEach(function (container) {
        const slug = container.getAttribute('data-simulation-slug');
        const stars = container.querySelectorAll('.star');
        const avgDisplay = container.querySelector('.star-avg');
        const countDisplay = container.querySelector('.star-count');
        let userRating = null;

        // Charge la note moyenne et la note utilisateur
        fetch(`/api/simulations/${slug}/rating`)
            .then(resp => resp.json())
            .then(data => {
                updateStars(data.user_rating);
                avgDisplay.textContent = data.average ? `${data.average} / 5` : '-';
                countDisplay.textContent = data.count ? `${data.count} votes` : '0 vote';
                userRating = data.user_rating;
            });

        // Interaction utilisateur UNIQUEMENT si le conteneur a l'attribut data-interactive
        if (container.hasAttribute('data-interactive')) {
            let pendingRating = null;
            let submitted = false;
            // Créer le bouton de validation
            const submitBtn = document.createElement('button');
            submitBtn.textContent = 'Valider mon choix';
            submitBtn.className = 'btn btn-success btn-sm ml-2';
            submitBtn.style.marginTop = '5px';
            submitBtn.disabled = true;
            container.appendChild(document.createElement('br'));
            container.appendChild(submitBtn);

            stars.forEach(function (star, idx) {
                star.addEventListener('mouseenter', function () {
                    if (!submitted) updateStars(idx + 1);
                });
                star.addEventListener('mouseleave', function () {
                    if (!submitted) updateStars(pendingRating || userRating);
                });
                star.addEventListener('click', function () {
                    if (submitted) return;
                    pendingRating = idx + 1;
                    updateStars(pendingRating);
                    submitBtn.disabled = false;
                    console.log('Note sélectionnée : ' + pendingRating);
                });
            });

            submitBtn.addEventListener('click', function () {
                if (submitted || !pendingRating) return;
                submitBtn.disabled = true;
                if (!pendingRating || pendingRating < 1 || pendingRating > 5) {
                    Swal.fire({ icon: 'error', toast: true, position: 'top-end', title: 'Veuillez sélectionner une note valide avant de valider.', showConfirmButton: false, timer: 2000 });
                    return;
                }
                console.log('Envoi de la note : ' + pendingRating);
                console.log('CSRF Token avant envoi (POST):', csrfToken);
                fetch(`/api/simulations/${slug}/rate`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Requested-With': 'XMLHttpRequest',
                        'X-CSRFToken': csrfToken,
                    },
                    body: JSON.stringify({ rating: pendingRating })
                })
                .then(async resp => {
                    // Si la réponse n'est pas JSON, c'est probablement une erreur d'auth ou serveur
                    let data;
                    try {
                        data = await resp.json();
                    } catch (e) {
                        throw new Error('Réponse du serveur inattendue (êtes-vous connecté ?).');
                    }
                    return data;
                })
                .then(data => {
                    if (data.status === 'success') {
                        userRating = pendingRating;
                        updateStars(userRating);
                        submitted = true;
                        Swal.fire({ icon: 'success', toast: true, position: 'top-end', title: 'Merci pour votre vote !', showConfirmButton: false, timer: 2000 });
                        submitBtn.textContent = 'Merci pour votre vote !';
                        submitBtn.classList.remove('btn-success');
                        submitBtn.classList.add('btn-secondary');
                        submitBtn.disabled = true;
                        // Désactiver les interactions
                        stars.forEach(star => {
                            star.style.pointerEvents = 'none';
                            star.style.cursor = 'default';
                        });
                        // Refresh moyenne et nombre de votes
                        console.log('CSRF Token avant envoi (POST):', csrfToken);
                        fetch(`/api/simulations/${slug}/rating`)
                            .then(resp => resp.json())
                            .then(data => {
                                avgDisplay.textContent = data.average ? `${data.average} / 5` : '-';
                                countDisplay.textContent = data.count ? `${data.count} votes` : '0 vote';
                            });
                    } else {
                        Swal.fire({ icon: 'error', toast: true, position: 'top-end', title: data.message || "Erreur lors de l'enregistrement de la note.", showConfirmButton: false, timer: 3000 });
                        submitBtn.disabled = false;
                    }
                })
                .catch(err => {
                    Swal.fire({ icon: 'error', toast: true, position: 'top-end', title: 'Erreur lors de la soumission : ' + err.message, showConfirmButton: false, timer: 3000 });
                    submitBtn.disabled = false;
                });
            });
        }

        /**
         * Met à jour l'état visuel des étoiles.
         * @param {number|null} rating - Note à afficher (1-5) ou null pour réinitialiser.
         */
        function updateStars(rating) {
            stars.forEach(function (star, i) {
                if (rating && i < rating) {
                    star.classList.add('fas', 'text-warning');
                    star.classList.remove('far', 'text-secondary');
                } else {
                    star.classList.remove('fas', 'text-warning');
                    star.classList.add('far', 'text-secondary');
                }
            });
        }
    });
});
