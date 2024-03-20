
-- --------------------------------------------------------

--
-- Structure de la table `Acces`
--

CREATE TABLE `Acces` (
  `id` int(11) NOT NULL,
  `prenom` varchar(20) NOT NULL,
  `login` varchar(20) NOT NULL,
  `password` varchar(20) NOT NULL,
  `statut` varchar(20) NOT NULL,
  `age` int(5) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Déchargement des données de la table `Acces`
--

INSERT INTO `Acces` (`id`, `prenom`, `login`, `password`, `statut`, `age`) VALUES
(1, 'Tom', 'tomahawk', 'indien', 'Etudiant', 22),
(2, 'Pierre', 'Pierrot', 'delalune', 'Prof', 44),
(3, 'Michel', 'lamere', 'sonchat', 'Admin', 69),
(4, 'Robin', 'Locksley', 'desbois', 'Etudiant', 23);

-- --------------------------------------------------------

--
-- Structure de la table `Statut`
--

CREATE TABLE `Statut` (
  `id` int(11) NOT NULL,
  `nom` varchar(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

--
-- Déchargement des données de la table `Statut`
--

INSERT INTO `Statut` (`id`, `nom`) VALUES
(1, 'Etudiant'),
(2, 'Prof'),
(3, 'Admin'),
(4, 'Visiteur');

--
-- Index pour les tables déchargées
--

--
-- Index pour la table `Acces`
--
ALTER TABLE `Acces`
  ADD PRIMARY KEY (`id`);

--
-- Index pour la table `Statut`
--
ALTER TABLE `Statut`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT pour les tables déchargées
--

--
-- AUTO_INCREMENT pour la table `Acces`
--
ALTER TABLE `Acces`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT pour la table `Statut`
--
ALTER TABLE `Statut`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
