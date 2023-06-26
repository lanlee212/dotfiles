# Edit this configuration file to define what should be installed on
# your system.  Help is available in the configuration.nix(5) man page
# and in the NixOS manual (accessible by running ‘nixos-help’).

{ config, pkgs, ... }:

{
  imports =
    [ # Include the results of the hardware scan.
      ./hardware-configuration.nix
    ];

  # Bootloader.
  boot.loader.systemd-boot.enable = true;
  boot.loader.efi.canTouchEfiVariables = true;

  networking.hostName = "nixos_laptop"; # Define your hostname.
  # networking.wireless.enable = true;  # Enables wireless support via wpa_supplicant.

  # Configure network proxy if necessary
  # networking.proxy.default = "http://user:password@proxy:port/";
  # networking.proxy.noProxy = "127.0.0.1,localhost,internal.domain";

  # Enable networking
  networking.networkmanager.enable = true;

  # Set your time zone.
  time.timeZone = "America/Chicago";

  # Select internationalisation properties.
  i18n.defaultLocale = "en_US.UTF-8";

  i18n.extraLocaleSettings = {
    LC_ADDRESS = "en_US.UTF-8";
    LC_IDENTIFICATION = "en_US.UTF-8";
    LC_MEASUREMENT = "en_US.UTF-8";
    LC_MONETARY = "en_US.UTF-8";
    LC_NAME = "en_US.UTF-8";
    LC_NUMERIC = "en_US.UTF-8";
    LC_PAPER = "en_US.UTF-8";
    LC_TELEPHONE = "en_US.UTF-8";
    LC_TIME = "en_US.UTF-8";
  };

  # Configure keymap in X11
  services.xserver = {
    enable = true;
    videoDrivers = ["modesettings"];
    layout = "us";
    xkbVariant = "";
   # desktopManager.cinnamon = {
   #   enable = true;
   # };
    windowManager.qtile = {
     enable = true;
     extraPackages =
  python3Packages: with python3Packages;[
         qtile-extras
         pyxdg
         dbus-next

     ];
  };
  displayManager = {
    lightdm.enable = true;
    lightdm.greeters.slick.enable = true;
    defaultSession = "none+qtile";
    };
  };
  # Define a user account. Don't forget to set a password with ‘passwd’.
  users.users.lee = {
    isNormalUser = true;
    description = "lee";
    extraGroups = [ "networkmanager" "wheel" ];
    packages = with pkgs; [];
  };

  # Allow unfree packages
  nixpkgs.config.allowUnfree = true;
  #hardware.opengl.extraPackages = [
  #	intel-compute-runtime
  #	intel-media-driver
  # ];
  # List packages installed in system profile. To search, run:
  # $ nix search wget
  environment.systemPackages = with pkgs; [
  #  vim # Do not forget to add an editor to edit configuration.nix! The Nano editor is also installed by default.
  #  wget
    firefox
    nitrogen
    rofi
    dunst
    alacritty
    git
    picom
    xdg-user-dirs
    vscodium
    neofetch
    cinnamon.nemo
    cinnamon.nemo-fileroller
    gnome.file-roller
    lxappearance
    arc-theme
    arc-icon-theme
    discord
    libsForQt5.kdeconnect-kde
    python311Packages.pyxdg
    python311Packages.dbus-next
    remmina
    megasync
  ];
  fonts.fonts = with pkgs; [
    ubuntu_font_family
    source-code-pro
    (nerdfonts.override { fonts = [ "NerdFontsSymbolsOnly" "Ubuntu" ]; })
];
  qt.enable = true;
    qt.platformTheme = "gtk2";
    qt.style = "gtk2";
  

nixpkgs.overlays = [

(self: super: {qtile = super.qtile.overrideAttrs(oldAttrs: {

pythonPath = oldAttrs.pythonPath ++ (with self.python311Packages;[

keyring

xcffib

setuptools

setuptools_scm

dateutil

dbus-python

dbus-next

xdg

mpd2

psutil

pyxdg

pygobject3

]);

});

})

]; 
  
hardware.bluetooth.enable = true;
programs.nm-applet.enable = true;
  # Some programs need SUID wrappers, can be configured further or are
  # started in user sessions.
  # programs.mtr.enable = true;
  # programs.gnupg.agent = {
  #   enable = true;
  #   enableSSHSupport = true;
  # }; 

  # List services uthat you want to enable:

  # Enable the OpenSSH daemon.
  # services.openssh.enable = true;

  # Open ports in the firewall.
  # networking.firewall.allowedTCPPorts = [ ... ];
  # networking.firewall.allowedUDPPorts = [ ... ];
  # Or disable the firewall altogether.
  networking.firewall.enable = false;

  # This value determines the NixOS release from which the default
  # settings for stateful data, like file locations and database versions
  # on your system were taken. It‘s perfectly fine and recommended to leave
  # this value at the release version of the first install of this system.
  # Before changing this value read the documentation for this option
  # (e.g. man configuration.nix or on https://nixos.org/nixos/options.html).
  system.stateVersion = "23.05"; # Did you read the comment?

}
