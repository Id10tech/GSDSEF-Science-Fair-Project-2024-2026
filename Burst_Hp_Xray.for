   	Subroutine Burst_HP_XRay_	! Drives HP 33210a 10.MHz Function /Arbitrary Waveform Generator
				!               is 50.MSa/s * 8kWords
				! For Lucas Chen

	Parameter  mxYL =   1024
	Parameter  mxYD = 8*mxYL,   pi = 3.14159265358979, tpi =2.*pi, pih = pi/2.
	Real  yDat(mxYD)
	Include 'gSouB:kc_Colors.par'
	Include 'gSouB:vt_Bold_cN.cmn'

	Character    cOut*960,        cRecV*96
	Character    cc*2 / ', ' /
	Byte               bOut(960),       bRecV(96)
	Equivalence (cOut, bOut ),   (cRecV,bRecV)
	Integer str$Position
	Data  isNewArr / .True. /

	Data iadHPfg / 10 /
	Dimension XRDat(20), XRDa2(20)
	Data  XRDat / 473, 44.1, 130, -432, 44.1, 251, 619,  840, 575, 513,
	2              0,   -436, -919, -1110, -1160,  -684, -2.3, 383, 578,  295 /
	Data  XRDa2 / 117, -95.2, -277, -169, -318, -183, -196, -330, -256, -179,
	2             -267, 81.1, 71.4, 292, 290, 403, 305, 264, 331, 116 /
	Include 'gSouR:[gpib]ibAttachC.cmn/list'

	               ios=1
	call QuestInp( ios, 'gSou:Burst_HP_XRay.for', 'New', *4 )

4	type *;  type *, 'Burst_HP_XRay  Reset  ====================================='
	kprIB = 20
	iadHPfg = iGet_Integer( 'GPIB iadHPfg  ( 1-31,   0->Emulate ) :', iadHPfg )
	if( iadHPfg.le.0 ) GoTo 900
	      cnIBQcal = 'BurstHP0'
	Call ibSDC( iadHPfg )
	                    !12345678901234567890
	             cOut = '*RST'
	Call ibSEOI( bOut, 4, iadHPfg )
	             cOut = '*CLS'
	Call ibSEOI( bOut, 4, iadHPfg );  if(kPr.ge.20) write(*,'(1x,a)') cOut(1:96)

cx	Call SetUGi( 3, 0,0, ' ' )
	type *, 'Initial Clear Complete'

	Data            iWavType /  1 /
	type*
	type *, 'Burst_HP_XRay  Generates an Wolff XRay Data repetitively'
	type *, '          on the HP 33120a Function/ArbWave Generator, using GPIB'
	type *, '  HP_fSampKHz = fSinKHz               /nCycSin *nPtsInWF'
	type *, '                fSinKHz = HP_fSampKHz *nCycSin /nPtsInWF'
	type *, '  HP displays fSampKHz, which can be changed manually after WaveForm.Download'
	type *, '              fSampKHz <= 50 000 from hardware limits.' 


5	Continue
10	type*;write(*,'(a)') '================  Rounded Burst ==============================================='
c? nPtsInWF  #.Points               in Waveform
c? nCycSin #.Cycles of Sin.Wave in Waveform
c? fSinKHz    freq  of Sin.Wav in kHz
c? fraRnd     fraction (begin & end) devoted to sin**2 Rounding (up then down)
c? AmpMax   Amplitude.Maximum (0-pk) for sine waves
c? iArrow   ?Arrow_Keys change  1=fSinKHz  2=AmpMax  <Rtn>Actuates   Off-Digits->Exit
c? nSinWavs #.Sine.Waves :  Normally 1;  but can add 2nd "Ticker" Wave" with rAmpTW & rFrqTW & PhopTW
c? lRevers  ? Reverse by 180deg after nCycSin/2, do nCycSin/2 more
	Data kPosFrRi / 0 /
	                 nPtI = nPtsInWF
	Data                    nPtsInWF,  nCycSin,  fSinKHz, fraRnd, AmpMax, iArrow, nSinWavs,    kPr, lRevers
	1/                       20,       20,       10.,    .25,    1.0,      0,        1,     20,  .False./
	iv=1; cN(iv) =       '  nPtsInWF   nCycSin   fSinKHz, fraRnd  AmpMax  iArrow; nSinWavs     kPr  lRevers'
	write(cD(iv),51)        nPtsInWF,  nCycSin,  fSinKHz, fraRnd, AmpMax, iArrow, nSinWavs,    kPr, lRevers
51	format(                   i10,      i10,    f10.2,   f8.2,   f8.3,   i8,   i10,         i8,  L9    )
	Call vt_Bold_Wr_cN_cD_CcV_BkpQ( iv, 1 )
	read (*,*,iostat=ios)   nPtI,  nCycSin,  fSinKHz, fraRnd, AmpMax, iArrow, nSinWavs,    kPr, lRevers
	                    if( nPtI.le.0 ) then;  type *, 'Re-Starting ...';   GoTo 4
	                                    else;  nPtsInWF =nPtI;  endif
	                     if(nPtsInWF.gt.1) nPtsInWF = max( 16, min( mxYD, nPtsInWF ) )
	                                                  fraRnd = max( 0.01, min( 0.5, fraRnd ) )
	                                                          AmpMax = max( .001, min( 5., AmpMax  ) )
	                                                                               kprIB = kPr -10
	write(cV(iv),51)        nPtsInWF,  nCycSin,  fSinKHz, fraRnd, AmpMax, iArrow, nSinWavs,    kPr, lRevers
	Call vt_Bold_Wr_cN_cB( iv )
	Call QuestInp( ios, 'gSou:Burst_HP.for', cN(iv), *10 )

	If( iGetYNy( 'Use 2nd Pulsar ?' ) ) XRDat = XRDa2

	Do  ip = 1, nPtsInWF
	  yDat(ip) = XRDat(ip)
	  yMax = max( yMax, abs(yDat(ip)) )
	EndDo
	if( yMax.gt.1. ) Then;   type*, 'Re-Normalizing Data to yMax=1.0'
	    yDat = yDat /yMax;   endif

1000	Call plu_WinN_Spec( 1, 'bHP_Wave', 625, 500 )
	                    xPts = nPtsInWF
	Call pluLabBox( 0., xPts,  -1., 1.,  .True., 3,3, 4,4,  'XRays' )
	Call pluY     ( yDat, 1, nPtsInWF,  kcBlack )
	Call plureLabY2( -AmpMax, AmpMax )
	
	If( iArrow.eq.0 ) Then 
	  If( .not.iGetYNy( 'Proceed to GPIB DownLoad?' ) ) GoTo 5
	EndIf

	Pause ! ------------------------

	kprIB = kPr -10

	            cnIBQcal = 'BurstHP1'
	                    !12345678901234567890
	             cOut = 'Data Volatile,'
	Call ibSend( bOut, 14, iadHPfg );   if(kPr.ge.20) write(*,'(1x,a)') cOut(1:96)

	                                 nDPG =80	! nData.Pts.Per.GPIBwrite
	Do ili = 1, mxYL;  ibp = (ili-1)*nDPG +1;  if(ibp.gt.nPtsInWF) Exit
	                   iep = min( nPtsInWF, ibp +nDPG-1 )
	          lLast = (iep.eq.nPtsInWF)
	             nf = iep - ibp +1
	             nc =10*nf
	                      write(cOut,1201) ((yDat(ii), cc),ii = ibp,iep )
	  if(.not.lLast) then; Call ibSend( bOut, nc,   iadHPfg )
	                 else; Call ibSEOI( bOut, nc-2, iadHPfg )
	  endif
1201	  format( <nf>(f8.4,a2) )
	  if(kPr.ge.20) write(*,'(1x,a)') cOut(1:96)
	EndDo
	type *, 'Data Download complete'

	            cnIBQcal = 'BurstHP2'
	                    !123456789012345678901234567890
	             cOut = 'Data:Copy Pulse, Volatile '
	Call ibSEOI( bOut, 26, iadHPfg );   if(kPr.ge.20) write(*,'(1x,a)') cOut(1:26)

	                    !123456789012345678901234567890
	             cOut = 'Func:User Pulse '
	Call ibSEOI( bOut, 26, iadHPfg );   if(kPr.ge.20) write(*,'(1x,a)') cOut(1:26)

	                        !123456789012345678901234567890
	                 cOut = 'SYST:ERR? '         ;  if(kPr.ge.20) write(*,'(1x,a)') cOut(1:96)
	  Call   ibSEOI( bOut, 10, iadHPfg )
	                 cOut = 'SYST:ERR? '         ;  if(kPr.ge.20) write(*,'(1x,a)') cOut(1:96)
	  Call   ibSEOI( bOut, 10, iadHPfg )
	  nByt = ibRecV(        bRecV, 96, iadHPfg )
	                               If( iadHPfg.le.0 ) GoTo 1410
	    ipE = str$Position( cRecV, 'No err' )
	          if(ipE.le.0 .or.(kEr.eq.1.and.kPr.ge.20)) write(*,'(1x,a)') cRecV(1:nByt)
	          if(ipE.le.0 ) type *, '********** Error *************'

	                    !123456789012345678901234567890
	             cOut = 'Func:Shap USER'
	Call ibSEOI( bOut, 14, iadHPfg );   if(kPr.ge.20) write(*,'(1x,a)') cOut(1:14)

	                    !123456789012345678901234567890
	             cOut = 'Trig:Sour IMM '
	Call ibSEOI( bOut, 14, iadHPfg );   if(kPr.ge.15) write(*,'(1x,a)') cOut(1:14)


	                        !123456789012345678901234567890
	                 cOut = 'SYST:ERR? '         ;  if(kPr.ge.20) write(*,'(1x,a)') cOut(1:96)
	  Call   ibSEOI( bOut, 10, iadHPfg )
	  nByt = ibRecV(        bRecV, 96, iadHPfg )
	                               If( iadHPfg.le.0 ) GoTo 1410
	    ipE = str$Position( cRecV, 'No err' )
	          if(ipE.le.0 .or.(kEr.eq.1.and.kPr.ge.20)) write(*,'(1x,a)') cRecV(1:nByt)
	          if(ipE.le.0 ) type *, '********** Error *************'

	                    !123456789012345678901234567890
	             cOut = 'BM:Stat ON'
	Call ibSEOI( bOut, 10, iadHPfg );   if(kPr.ge.20) write(*,'(1x,a)') cOut(1:10)

	                    !123456789012345678901234567890
	             cOut = 'BM:INT:RATE 499 Hz'
	Call ibSEOI( bOut, 18, iadHPfg );   if(kPr.ge.15) write(*,'(1x,a)') cOut(1:18)

	                        !123456789012345678901234567890
	                 cOut = 'SYST:ERR? '         ;  if(kPr.ge.20) write(*,'(1x,a)') cOut(1:96)
	  Call   ibSEOI( bOut, 10, iadHPfg )
	  nByt = ibRecV(        bRecV, 96, iadHPfg )
	                               If( iadHPfg.le.0 ) GoTo 1410
	    ipE = str$Position( cRecV, 'No err' )
	          if(ipE.le.0 .or.(kEr.eq.1.and.kPr.ge.20)) write(*,'(1x,a)') cRecV(1:nByt)
	          if(ipE.le.0 ) type *, '********** Error *************'

	                    !123456789012345678901234567890
	             cOut = 'Volt:Unit VPP '
	Call ibSEOI( bOut, 14, iadHPfg );   if(kPr.ge.20) write(*,'(1x,a)') cOut(1:14)


1300	If    ( iWavType .eq. 1 ) Then;  frqRptKHz = fSinKHz /nCycSin
	ElseIf( iWavType .eq. 2 ) Then;  frqRptKHz = 1. / tTotMS
	EndIf

	write(*,1301)              nPtsInWF,  frqRptKHz,   AmpMax
1301	format(                 '  nPtsInWF   frqRptKHz    AmpMax' / i10, f12.3, f10.3 )

	If( frqRptKHz .gt. 50.e3 ) Then
	    type*, '*** Error  HP.33120 Max frqRptKHz =50,000 /nPtsInWF ***'
	    if( iWavType.eq.1 ) type*, '*** frqRptKHz = fSinKHz /nCycSin ***'
	    if( iWavType.eq.2 ) type*, '*** frqRptKHz = 1. /tTotMS ***'
	  GoTo 4
	Else;                      frqRpt = frqRptKHz *1e3
	EndIF	

	            cnIBQcal = 'BurstHP3'
	                                  !123456789012345678901234567890
	      write( cOut, '(a5,f8.3)'  ) 'Volt ', 2*AmpMax
	Call ibSEOI( bOut, 12, iadHPfg );   if(kPr.ge.20) write(*,'(1x,a)') cOut(1:12)

	                    !123456789012345678901234567890
	             cOut = 'FREQ 1234567890 '
	       write(cOut(6:15),'(f10.2)') 500.
	Call ibSEOI( bOut, 16, iadHPfg );  if(kPr.ge.20) write(*,'(1x,a)') cOut(1:96)

	type *, 'Command Download complete'
	            cnIBQcal = 'BurstHP4'

	Do 1400 kEr = 1, 20
	                        !123456789012345678901234567890
	                 cOut = 'SYST:ERR? '         ;  if(kPr.ge.20) write(*,'(1x,a)') cOut(1:96)
	  Call   ibSEOI( bOut, 10, iadHPfg )
	  nByt = ibRecV(        bRecV, 96, iadHPfg )
	                               If( iadHPfg.le.0 ) GoTo 1410
	    ipE = str$Position( cRecV, 'No err' )
	          if(ipE.le.0 .or.(kEr.eq.1.and.kPr.ge.20)) write(*,'(1x,a)') cRecV(1:nByt)
	          if(ipE.le.0 ) type *, '********** Error *************'
	if( ipE .gt. 0 ) GoTo 1410                   
1400	Continue
1410	type *, 'Error   Check    complete'

	If( iArrow.eq.1   ) Then;  If( isNewArr ) Then;  isNewArr = .False.
	                               type*; type*, 'Arrow Lef,Rig TO      Digit;   <Rtn> Actuates New Values'
                                       type*, '      Up, Dn  CHANGES Digit;   <Rtn>.Off.Digits  -> EXIT';  type*
	                           EndIf
	  Call g_Arrow_Key_Real( fSinKHz, 'fSinKHz', 3,       kPosFrRi )
	                         fSinKHz = abs(fSinKHz);  if( kPosFrRi.eq.0 ) iArrow = 0
	  GoTo 1300
	EndIf

	If( iArrow.eq.2   ) Then;  type *
	  Call g_Arrow_Key_Real( AmpMax, 'AmpMax', 3,       kPosFrRi )
	                         AmpMax = abs(AmpMax);  if( kPosFrRi.eq.0 ) iArrow = 0
	  GoTo 1300
	EndIf

	if( iWavType.eq.1 ) GoTo 10
	GoTo 5

900	type*, 'Returning from Burst_HP_ ...'
	Return
	End
