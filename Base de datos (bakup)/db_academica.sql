-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 21-10-2025 a las 17:28:46
-- Versión del servidor: 10.4.32-MariaDB
-- Versión de PHP: 8.0.30

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `db_academica`
--
CREATE DATABASE IF NOT EXISTS `db_academica` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE `db_academica`;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `alumnos`
--

DROP TABLE IF EXISTS `alumnos`;
CREATE TABLE IF NOT EXISTS `alumnos` (
  `idAlumno` int(10) NOT NULL AUTO_INCREMENT,
  `codigo` char(10) NOT NULL,
  `nombre` char(100) NOT NULL,
  `direccion` char(150) NOT NULL,
  `telefono` char(10) NOT NULL,
  `email` char(100) NOT NULL,
  PRIMARY KEY (`idAlumno`)
) ENGINE=InnoDB AUTO_INCREMENT=40 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `alumnos`
--

INSERT INTO `alumnos` (`idAlumno`, `codigo`, `nombre`, `direccion`, `telefono`, `email`) VALUES
(28, 'USIS018804', 'lolita Gonita preciosas', 'Puerto la Libertad', '0000-0000', 'uuuu@GMAIL.COM'),
(30, '848823', 'Petuni Putinia', 'Rosado negro', '223232-434', 'sQ}@ds.xs'),
(38, 'USSA112587', 'Soberana Martinez', 'dshjsd@gmail.com', '1234-8894', 'ghagsh@gmail.com'),
(39, 'UAPA323698', 'Juan Perez Romero', 'Sivar', '22587-6695', 'sahsh@gmail.com');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `docentes`
--

DROP TABLE IF EXISTS `docentes`;
CREATE TABLE IF NOT EXISTS `docentes` (
  `idDocente` int(11) NOT NULL AUTO_INCREMENT,
  `codigo` varchar(20) NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `direccion` varchar(255) DEFAULT NULL,
  `telefono` varchar(15) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `dui` varchar(10) NOT NULL,
  `escalafon` varchar(50) NOT NULL,
  PRIMARY KEY (`idDocente`),
  UNIQUE KEY `codigo` (`codigo`),
  UNIQUE KEY `dui` (`dui`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=59 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `docentes`
--

INSERT INTO `docentes` (`idDocente`, `codigo`, `nombre`, `direccion`, `telefono`, `email`, `dui`, `escalafon`) VALUES
(42, 'USSSS52144', 'Eva Martinez', 'Usulutan', '2223-3244', 'Eadsa@gmail.com', '21112226-5', '520028'),
(51, 'USSS354458', 'Rosa Maria Pachita', 'usuluteca', '2232-3243', 'romero@gmail.com', '00455454-5', '1000'),
(55, 'USSUA25589', 'Butera Nicolle', 'Comunidad LGBTQ+', '6698-7744', 'gonitaUWu@gmail.com', '00258875-2', '300'),
(57, 'CIAO212154', 'Manito Romino', 'La colonia de romeor', '7895-2227', 'bjsn@gmail.com', '33322554-4', '120'),
(58, 'UAOQ445544', 'Mundo Reyes Gonito', 'Usulutan', '4123-2448', 'romero1@gmail.com', '44668884-7', '1236');

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `materias`
--

DROP TABLE IF EXISTS `materias`;
CREATE TABLE IF NOT EXISTS `materias` (
  `idMateria` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `codigo` varchar(20) NOT NULL,
  `idDocente` int(11) DEFAULT NULL,
  PRIMARY KEY (`idMateria`),
  UNIQUE KEY `codigo` (`codigo`),
  KEY `idDocente` (`idDocente`)
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `materias`
--

INSERT INTO `materias` (`idMateria`, `nombre`, `codigo`, `idDocente`) VALUES
(4, 'Física Apliacada I', 'FIS203', 42),
(5, 'Química General', 'QUI301', 51),
(6, 'Programación Avanzada', 'PRO401', 51),
(11, 'Ing. de Software y Backend', 'PES777', 55),
(12, 'Teoria de Genero desde la FIlosofia aplicada', 'OSI228', 55),
(14, 'Cotejo21', 'AHS239', 57),
(16, 'Rospas', 'USA258', 58);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `notas`
--

DROP TABLE IF EXISTS `notas`;
CREATE TABLE IF NOT EXISTS `notas` (
  `idNota` int(11) NOT NULL AUTO_INCREMENT,
  `idAlumno` int(11) DEFAULT NULL,
  `idMateria` int(11) DEFAULT NULL,
  `nota` decimal(5,2) DEFAULT NULL,
  `aprobado` varchar(2) GENERATED ALWAYS AS (case when `nota` >= 6 then 'SI' else 'NO' end) STORED,
  PRIMARY KEY (`idNota`),
  KEY `idAlumno` (`idAlumno`),
  KEY `idMateria` (`idMateria`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `notas`
--

INSERT INTO `notas` (`idNota`, `idAlumno`, `idMateria`, `nota`) VALUES
(5, 28, 4, 4.00),
(6, 28, 5, 6.90),
(10, 38, 11, 10.00),
(11, 38, 14, 38.00);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuarios`
--

DROP TABLE IF EXISTS `usuarios`;
CREATE TABLE IF NOT EXISTS `usuarios` (
  `idUsuario` int(10) NOT NULL AUTO_INCREMENT,
  `usuario` char(35) NOT NULL,
  `clave` char(35) NOT NULL,
  `nombre` char(85) NOT NULL,
  `direccion` char(100) DEFAULT NULL,
  `telefono` char(9) DEFAULT NULL,
  PRIMARY KEY (`idUsuario`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `usuarios`
--

INSERT INTO `usuarios` (`idUsuario`, `usuario`, `clave`, `nombre`, `direccion`, `telefono`) VALUES
(1, 'jdoe', 'abc123', 'John Doe', 'Av. Principal 123', '712345678');

-- --------------------------------------------------------

--
-- Estructura Stand-in para la vista `vista_materias`
-- (Véase abajo para la vista actual)
--
DROP VIEW IF EXISTS `vista_materias`;
CREATE TABLE IF NOT EXISTS `vista_materias` (
`idMateria` int(11)
,`nombre_materia` varchar(100)
,`codigo` varchar(20)
,`nombre_docente` varchar(100)
);

-- --------------------------------------------------------

--
-- Estructura Stand-in para la vista `vista_notas`
-- (Véase abajo para la vista actual)
--
DROP VIEW IF EXISTS `vista_notas`;
CREATE TABLE IF NOT EXISTS `vista_notas` (
`nombre_alumno` char(100)
,`nombre_materia` varchar(100)
,`nota` decimal(5,2)
);

-- --------------------------------------------------------

--
-- Estructura para la vista `vista_materias`
--
DROP TABLE IF EXISTS `vista_materias`;

DROP VIEW IF EXISTS `vista_materias`;
CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `vista_materias`  AS SELECT `m`.`idMateria` AS `idMateria`, `m`.`nombre` AS `nombre_materia`, `m`.`codigo` AS `codigo`, `d`.`nombre` AS `nombre_docente` FROM (`materias` `m` left join `docentes` `d` on(`m`.`idDocente` = `d`.`idDocente`)) ;

-- --------------------------------------------------------

--
-- Estructura para la vista `vista_notas`
--
DROP TABLE IF EXISTS `vista_notas`;

DROP VIEW IF EXISTS `vista_notas`;
CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `vista_notas`  AS SELECT `a`.`nombre` AS `nombre_alumno`, `m`.`nombre` AS `nombre_materia`, `n`.`nota` AS `nota` FROM ((`notas` `n` join `alumnos` `a` on(`n`.`idAlumno` = `a`.`idAlumno`)) join `materias` `m` on(`n`.`idMateria` = `m`.`idMateria`)) ;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `materias`
--
ALTER TABLE `materias`
  ADD CONSTRAINT `materias_ibfk_1` FOREIGN KEY (`idDocente`) REFERENCES `docentes` (`idDocente`);

--
-- Filtros para la tabla `notas`
--
ALTER TABLE `notas`
  ADD CONSTRAINT `notas_ibfk_1` FOREIGN KEY (`idAlumno`) REFERENCES `alumnos` (`idAlumno`),
  ADD CONSTRAINT `notas_ibfk_2` FOREIGN KEY (`idMateria`) REFERENCES `materias` (`idMateria`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
