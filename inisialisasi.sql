-- phpMyAdmin SQL Dump
-- version 5.0.2
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Jul 30, 2021 at 08:35 AM
-- Server version: 10.4.11-MariaDB
-- PHP Version: 7.4.5

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `absen_wajah`
--

-- --------------------------------------------------------

--
-- Table structure for table `absensi`
--

DROP TABLE IF EXISTS `absensi`;
CREATE TABLE `absensi` (
  `id_absensi` int(11) NOT NULL,
  `id_sesi_fk` int(11) NOT NULL,
  `id_mahasiswa_fk` int(11) NOT NULL,
  `waktu` datetime NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `kelas`
--

DROP TABLE IF EXISTS `kelas`;
CREATE TABLE `kelas` (
  `id_kelas` int(11) NOT NULL,
  `id_status_kelas` int(11) DEFAULT NULL,
  `nama_kelas` varchar(25) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `mahasiswa`
--

DROP TABLE IF EXISTS `mahasiswa`;
CREATE TABLE `mahasiswa` (
  `id_mahasiswa` int(11) NOT NULL,
  `id_kelas` int(11) NOT NULL,
  `nrp_mahasiswa` varchar(10) NOT NULL,
  `nama_mahasiswa` varchar(255) NOT NULL,
  `foto_mahasiswa` varchar(512) DEFAULT ''
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `mata_kuliah`
--

DROP TABLE IF EXISTS `mata_kuliah`;
CREATE TABLE `mata_kuliah` (
  `id_mata_kuliah` int(11) NOT NULL,
  `nama_mata_kuliah` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `mata_kuliah`
--

INSERT INTO `mata_kuliah` (`id_mata_kuliah`, `nama_mata_kuliah`) VALUES
(2, 'mata kuliah 1'),
(3, 'mata kuliah 2'),
(4, 'mk baru'),
(5, 'Mata Kuliah Baru'),
(6, 'Test'),
(7, 'Matematika');

-- --------------------------------------------------------

--
-- Table structure for table `pengguna`
--

DROP TABLE IF EXISTS `pengguna`;
CREATE TABLE `pengguna` (
  `id_pengguna` int(11) NOT NULL,
  `id_tipe_pengguna` int(11) NOT NULL,
  `email_pengguna` varchar(255) NOT NULL,
  `password_pengguna` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `pengguna`
--

INSERT INTO `pengguna` (`id_pengguna`, `id_tipe_pengguna`, `email_pengguna`, `password_pengguna`) VALUES
(1, 1, 'admin@admin.com', 'df620221097ec17a0106aace752a5822'),
(2, 2, 'pengajar1@pengajar.com', 'df620221097ec17a0106aace752a5822'),
(7, 2, 'pengajar2@pengajar.com', 'df620221097ec17a0106aace752a5822'),
(9, 2, 'pgn1@gmail.com', 'df620221097ec17a0106aace752a5822'),
(11, 2, 'dosen1@gmail.com', 'df620221097ec17a0106aace752a5822'),
(12, 2, 'fian@gmail.com', 'df620221097ec17a0106aace752a5822'),
(15, 2, 'em@gmail.com', 'df620221097ec17a0106aace752a5822'),
(16, 2, 'dosen@gmail.com', 'df620221097ec17a0106aace752a5822');

-- --------------------------------------------------------

--
-- Table structure for table `ruang`
--

DROP TABLE IF EXISTS `ruang`;
CREATE TABLE `ruang` (
  `id_ruang` int(11) NOT NULL,
  `nama_ruang` varchar(255) NOT NULL,
  `alamat_kamera` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `ruang`
--

INSERT INTO `ruang` (`id_ruang`, `nama_ruang`, `alamat_kamera`) VALUES
(1, 'ruang 1', '192.168.1.11:8080/video'),
(2, 'ruang 2', '192.168.1.3:8080/video'),
(6, 'ruang 3', '192.168.1.2:8080/video'),
(7, 'ruang rolag', '192.168.189.230:8080/video'),
(8, 'ruang percobaan', '192.168.1.6:8080/video'),
(9, 'S4', '192.168.1.12:8080/video');

-- --------------------------------------------------------

--
-- Table structure for table `sesi`
--

DROP TABLE IF EXISTS `sesi`;
CREATE TABLE `sesi` (
  `id_sesi` int(11) NOT NULL,
  `id_mata_kuliah_fk` int(11) NOT NULL,
  `id_pengguna` int(11) NOT NULL,
  `id_status_sesi` int(11) NOT NULL,
  `id_kelas` int(11) DEFAULT NULL,
  `nama_sesi` varchar(255) NOT NULL,
  `waktu_mulai_sesi` timestamp NOT NULL DEFAULT current_timestamp(),
  `id_ruang` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `status_kelas`
--

DROP TABLE IF EXISTS `status_kelas`;
CREATE TABLE `status_kelas` (
  `id_status_kelas` int(11) NOT NULL,
  `nama_status_kelas` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `status_kelas`
--

INSERT INTO `status_kelas` (`id_status_kelas`, `nama_status_kelas`) VALUES
(1, 'Belum siap'),
(2, 'Siap');

-- --------------------------------------------------------

--
-- Table structure for table `status_sesi`
--

DROP TABLE IF EXISTS `status_sesi`;
CREATE TABLE `status_sesi` (
  `id_status_sesi` int(11) NOT NULL,
  `nama_status_sesi` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `status_sesi`
--

INSERT INTO `status_sesi` (`id_status_sesi`, `nama_status_sesi`) VALUES
(1, 'Dibuka'),
(2, 'DiCapture'),
(3, 'Mengenali'),
(4, 'Dijeda'),
(5, 'Ditutup'),
(6, 'Ditutup');

-- --------------------------------------------------------

--
-- Table structure for table `tipe_pengguna`
--

DROP TABLE IF EXISTS `tipe_pengguna`;
CREATE TABLE `tipe_pengguna` (
  `id_tipe_pengguna` int(11) NOT NULL,
  `nama_tipe_pengguna` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `tipe_pengguna`
--

INSERT INTO `tipe_pengguna` (`id_tipe_pengguna`, `nama_tipe_pengguna`) VALUES
(1, 'Admin'),
(2, 'Pengajar');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `absensi`
--
ALTER TABLE `absensi`
  ADD PRIMARY KEY (`id_absensi`),
  ADD KEY `id_mahasiswa_fk` (`id_mahasiswa_fk`),
  ADD KEY `id_sesi_fk` (`id_sesi_fk`);

--
-- Indexes for table `kelas`
--
ALTER TABLE `kelas`
  ADD PRIMARY KEY (`id_kelas`),
  ADD KEY `id_status_kelas` (`id_status_kelas`);

--
-- Indexes for table `mahasiswa`
--
ALTER TABLE `mahasiswa`
  ADD PRIMARY KEY (`id_mahasiswa`),
  ADD KEY `id_kelas` (`id_kelas`);

--
-- Indexes for table `mata_kuliah`
--
ALTER TABLE `mata_kuliah`
  ADD PRIMARY KEY (`id_mata_kuliah`);

--
-- Indexes for table `pengguna`
--
ALTER TABLE `pengguna`
  ADD PRIMARY KEY (`id_pengguna`),
  ADD KEY `id_tipe_pengguna` (`id_tipe_pengguna`);

--
-- Indexes for table `ruang`
--
ALTER TABLE `ruang`
  ADD PRIMARY KEY (`id_ruang`);

--
-- Indexes for table `sesi`
--
ALTER TABLE `sesi`
  ADD PRIMARY KEY (`id_sesi`),
  ADD KEY `id_mata_kuliah_fk` (`id_mata_kuliah_fk`),
  ADD KEY `id_pengguna` (`id_pengguna`),
  ADD KEY `id_status_sesi` (`id_status_sesi`),
  ADD KEY `id_kelas` (`id_kelas`),
  ADD KEY `id_ruang` (`id_ruang`);

--
-- Indexes for table `status_kelas`
--
ALTER TABLE `status_kelas`
  ADD PRIMARY KEY (`id_status_kelas`);

--
-- Indexes for table `status_sesi`
--
ALTER TABLE `status_sesi`
  ADD PRIMARY KEY (`id_status_sesi`);

--
-- Indexes for table `tipe_pengguna`
--
ALTER TABLE `tipe_pengguna`
  ADD PRIMARY KEY (`id_tipe_pengguna`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `absensi`
--
ALTER TABLE `absensi`
  MODIFY `id_absensi` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `kelas`
--
ALTER TABLE `kelas`
  MODIFY `id_kelas` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `mahasiswa`
--
ALTER TABLE `mahasiswa`
  MODIFY `id_mahasiswa` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `mata_kuliah`
--
ALTER TABLE `mata_kuliah`
  MODIFY `id_mata_kuliah` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT for table `pengguna`
--
ALTER TABLE `pengguna`
  MODIFY `id_pengguna` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=17;

--
-- AUTO_INCREMENT for table `ruang`
--
ALTER TABLE `ruang`
  MODIFY `id_ruang` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

--
-- AUTO_INCREMENT for table `sesi`
--
ALTER TABLE `sesi`
  MODIFY `id_sesi` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `status_kelas`
--
ALTER TABLE `status_kelas`
  MODIFY `id_status_kelas` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `status_sesi`
--
ALTER TABLE `status_sesi`
  MODIFY `id_status_sesi` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT for table `tipe_pengguna`
--
ALTER TABLE `tipe_pengguna`
  MODIFY `id_tipe_pengguna` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `absensi`
--
ALTER TABLE `absensi`
  ADD CONSTRAINT `absensi_ibfk_2` FOREIGN KEY (`id_mahasiswa_fk`) REFERENCES `mahasiswa` (`id_mahasiswa`) ON DELETE CASCADE ON UPDATE NO ACTION,
  ADD CONSTRAINT `absensi_ibfk_3` FOREIGN KEY (`id_sesi_fk`) REFERENCES `sesi` (`id_sesi`) ON DELETE CASCADE ON UPDATE NO ACTION;

--
-- Constraints for table `kelas`
--
ALTER TABLE `kelas`
  ADD CONSTRAINT `kelas_ibfk_1` FOREIGN KEY (`id_status_kelas`) REFERENCES `status_kelas` (`id_status_kelas`);

--
-- Constraints for table `mahasiswa`
--
ALTER TABLE `mahasiswa`
  ADD CONSTRAINT `mahasiswa_ibfk_1` FOREIGN KEY (`id_kelas`) REFERENCES `kelas` (`id_kelas`) ON DELETE CASCADE ON UPDATE NO ACTION;

--
-- Constraints for table `pengguna`
--
ALTER TABLE `pengguna`
  ADD CONSTRAINT `pengguna_ibfk_1` FOREIGN KEY (`id_tipe_pengguna`) REFERENCES `tipe_pengguna` (`id_tipe_pengguna`) ON DELETE NO ACTION ON UPDATE NO ACTION;

--
-- Constraints for table `sesi`
--
ALTER TABLE `sesi`
  ADD CONSTRAINT `sesi_ibfk_1` FOREIGN KEY (`id_mata_kuliah_fk`) REFERENCES `mata_kuliah` (`id_mata_kuliah`) ON DELETE CASCADE ON UPDATE NO ACTION,
  ADD CONSTRAINT `sesi_ibfk_2` FOREIGN KEY (`id_status_sesi`) REFERENCES `status_sesi` (`id_status_sesi`),
  ADD CONSTRAINT `sesi_ibfk_3` FOREIGN KEY (`id_pengguna`) REFERENCES `pengguna` (`id_pengguna`),
  ADD CONSTRAINT `sesi_ibfk_4` FOREIGN KEY (`id_kelas`) REFERENCES `kelas` (`id_kelas`),
  ADD CONSTRAINT `sesi_ibfk_5` FOREIGN KEY (`id_ruang`) REFERENCES `ruang` (`id_ruang`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
