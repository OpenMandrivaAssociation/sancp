%define _localstatedir %{_var}

Name:           sancp
Version:        1.6.1
Release:        %mkrel 3
Epoch:          0
Summary:        Security Analyst Network Connection Profiler 
License:        GPL
Group:          Networking/Other
URL:            http://www.metre.net/sancp.html
Source0:        http://www.metre.net/files/sancp-%{version}.tar.gz
Source1:        http://www.metre.net/files/sancp-%{version}.tar.gz.md5
Source2:        sancp.init
Source3:        sancp.logrotate
Patch0:         sancp-1.6.1.fix200511.a.patch
Patch1:         sancp-1.6.1.fix200511.b.patch
Patch2:         sancp-1.6.1.fix200601.c.patch
Patch3:         sancp-1.6.1.fix200606.d.patch
Patch4:         sancp-1.6.1-prelude.patch
Requires(post): rpm-helper
Requires(postun): rpm-helper
Requires(pre):  rpm-helper
Requires(preun): rpm-helper
BuildRequires:  pcap-devel
BuildRequires:  prelude-devel
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root

%description
This is a network security tool designed to collect statistical 
information regarding network traffic, as well as, collect the traffic 
itself in pcap format, all for the purpose of: auditing, historical 
analysis, and network activity discovery. Rules can be used to 
distinguish normal from abnormal traffic and support tagging 
connections with: rule id, node id, and status id. From an intrusion 
detection standpoint, every connection is an event that must be 
validated through some means. Sancp uses rules to identify, record, and 
tag traffic of interest. 'Tagging' a connection is a new feature since 
v1.4.0 Connections ('stats') can be loaded into a database for further 
analysis.

Sancp rules control three types of logging for a connection: pcap, 
stats, and realtime 'pcap' refers to packet data collected on the 
connection in tcpdump format, 'stats' refers to a single line summary 
of an entire connection once it is 'closed' 'realtime' is a snapshot of 
'stats' based on the initial packet, for immediate reporting Both 
'stats' and 'realtime' contain a number of fields used for recording 
packet statistics, TCP flags, p0f data, and other vitals about how we 
handle the connection.

%prep
%setup -q
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1

%build
%serverbuild
%{make} CFLAGS="%{optflags}"

%install
%{__rm} -rf %{buildroot}

%{__mkdir_p} %{buildroot}%{_bindir}
%{__cp} -a sancp %{buildroot}%{_bindir}/sancp

%{__mkdir_p} %{buildroot}%{_sysconfdir}/%{name}
%{__cp} -a etc/sancp/sancp.conf %{buildroot}%{_sysconfdir}/%{name}/sancp.conf

%{__mkdir_p} %{buildroot}%{_initrddir}
%{__cp} -a %{SOURCE2} %{buildroot}%{_initrddir}/%{name}

%{__mkdir_p} %{buildroot}%{_localstatedir}/lib/%{name}

%{__mkdir_p} %{buildroot}%{_logdir}/%{name}
/bin/touch %{buildroot}%{_logdir}/%{name}/sancp.log

%{__mkdir_p} %{buildroot}%{_sysconfdir}/logrotate.d
%{__cp} -a %{SOURCE3} %{buildroot}%{_sysconfdir}/logrotate.d/%{name}

%{__mkdir_p} %{buildroot}%{_sysconfdir}/sysconfig
%{__cat} > %{buildroot}%{_sysconfdir}/sysconfig/%{name} << EOF
#SANCP_INTERFACE="-i eth1"
EOF

%{__mkdir_p} %{buildroot}%{_sysconfdir}/prelude/profile/%{name}

%{__cat} > README.urpmi << EOF
Before the sancp service can start, you must add the sensor to
prelude with a command similar to the following:

%{_bindir}/prelude-adduser register sancp "idmef:w" localhost --uid sancp --gid sancp
EOF

%clean
%{__rm} -rf %{buildroot}

%pre
%_pre_useradd %{name} %{_localstatedir}/lib/%{name} /bin/bash
%_pre_groupadd %{name}

%preun
%_preun_service %{name}

%post
%create_ghostfile %{_logdir}/%{name}/sancp.log %{name} %{name} 0660
%_post_service %{name}

%postun
%_postun_userdel %{name}
%_postun_groupdel %{name}

%files
%defattr(0644,root,root,0755)
%doc LICENSE contrib docs/* README.urpmi
%attr(0755,root,root) %{_bindir}/sancp
%attr(0755,root,root) %{_initrddir}/%{name}
%attr(0700,sancp,sancp) %dir %{_localstatedir}/lib/%{name}
%attr(0750,sancp,sancp) %dir %{_logdir}/%{name}
%ghost %attr(0660,sancp,sancp) %dir %{_logdir}/%{name}/sancp.log
%dir %{_sysconfdir}/%{name}
%config(noreplace) %{_sysconfdir}/%{name}/sancp.conf
%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}
%config(noreplace) %{_sysconfdir}/sysconfig/%{name}
%dir %attr(0750,sancp,sancp) %{_sysconfdir}/prelude/profile/%{name}
