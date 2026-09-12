import java.io.File;
import java.io.FileNotFoundException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

import oasis.names.tc.xacml._3_0.core.schema.wd_17.Request;
import oasis.names.tc.xacml._3_0.core.schema.wd_17.Response;
import org.ow2.authzforce.core.pdp.api.XmlUtils.XmlnsFilteringParser;
import org.ow2.authzforce.core.pdp.api.io.PdpEngineInoutAdapter;
import org.ow2.authzforce.core.pdp.api.io.XacmlJaxbParsingUtils;
import org.ow2.authzforce.core.pdp.impl.PdpEngineConfiguration;
import org.ow2.authzforce.core.pdp.impl.io.PdpEngineAdapters;
import org.ow2.authzforce.core.pdp.testutil.TestUtils;
import org.springframework.util.ResourceUtils;

/**
 * Minimal native PDP runner for PC-XACML-S3+.
 *
 * <p>Evaluates one XACML request with the frozen AuthzForce PDP
 * configuration using exactly the same construction path as the upstream
 * conformance helper
 * ({@code XacmlXmlPdpTestHelper}): {@code PdpEngineConfiguration} from
 * {@code pdp.xml}, {@code PdpEngineAdapters.newXacmlJaxbInoutAdapter},
 * request parsing via {@code TestUtils.createRequest}. It performs no
 * authorization logic of its own: it only constructs the standard engine,
 * submits the standard request, and writes the returned standard
 * response. Arguments: {@code <fixtureDir> <requestFile>
 * <responseOutFile>} where {@code fixtureDir} holds {@code pdp.xml} and
 * {@code policies/} in the upstream layout.
 */
public final class PdpRunner
{
	private PdpRunner()
	{
		// utility class
	}

	/**
	 * Evaluates the request and writes the response XML.
	 *
	 * @param args fixture directory, request file, response output file
	 * @throws Exception on any evaluation or I/O failure
	 */
	public static void main(final String[] args) throws Exception
	{
		if (args.length != 3)
		{
			System.err.println("usage: PdpRunner <fixtureDir> <requestFile> <responseOutFile>");
			System.exit(2);
		}
		final Path fixtureDir = Paths.get(args[0]);
		final Path pdpConfFile = fixtureDir.resolve("pdp.xml");
		File pdpExtXsdFile = null;
		try
		{
			pdpExtXsdFile = ResourceUtils.getFile("classpath:pdp-ext.xsd");
		}
		catch (final FileNotFoundException e)
		{
			// Same behavior as XacmlXmlPdpTestHelper: proceed without extensions.
			System.out.println("PDP_RUNNER_INFO no pdp-ext.xsd on classpath, proceeding without extensions");
		}
		final PdpEngineConfiguration pdpEngineConf = pdpExtXsdFile == null
		        ? PdpEngineConfiguration.getInstance(pdpConfFile.toString())
		        : PdpEngineConfiguration.getInstance(pdpConfFile.toString(), "classpath:catalog.xml", "classpath:pdp-ext.xsd");
		final PdpEngineInoutAdapter<Request, Response> pdp = PdpEngineAdapters.newXacmlJaxbInoutAdapter(pdpEngineConf);
		final XmlnsFilteringParser unmarshaller = XacmlJaxbParsingUtils.getXacmlParserFactory(false).getInstance();
		final Request request = TestUtils.createRequest(Paths.get(args[1]), unmarshaller);
		final Response response = pdp.evaluate(request, null);
		final String xml = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n" + TestUtils.printResponse(response) + "\n";
		Files.write(Paths.get(args[2]), xml.getBytes(StandardCharsets.UTF_8));
		System.out.println("PDP_EVAL_OK response written");
	}
}
